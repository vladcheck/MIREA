import os
import secrets
from datetime import datetime, timedelta
import jwt
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPBearer, HTTPAuthorizationCredentials
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from passlib.context import CryptContext
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv

from models import User, UserInDB, TodoCreate, TodoUpdate, TodoResponse
from database import init_db, get_db_connection

load_dotenv()

MODE = os.getenv("MODE", "DEV")
if MODE not in ["DEV", "PROD"]:
    raise ValueError(f"Invalid MODE: {MODE}. Must be 'DEV' or 'PROD'.")

DOCS_USER = os.getenv("DOCS_USER", "admin")
DOCS_PASSWORD = os.getenv("DOCS_PASSWORD", "admin")
SECRET_KEY = os.getenv("SECRET_KEY", "secret_key")
ALGORITHM = "HS256"

init_db()

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

security_basic = HTTPBasic()
security_bearer = HTTPBearer()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_docs_credentials(credentials: HTTPBasicCredentials = Depends(security_basic)):
    correct_user = secrets.compare_digest(credentials.username, DOCS_USER)
    correct_password = secrets.compare_digest(credentials.password, DOCS_PASSWORD)
    if not (correct_user and correct_password):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.get("/docs", include_in_schema=False)
def get_docs(username: str = Depends(verify_docs_credentials) if MODE == "DEV" else None):
    if MODE == "PROD":
        raise HTTPException(status_code=404, detail="Not Found")
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Docs")

@app.get("/openapi.json", include_in_schema=False)
def get_openapi_endpoint(username: str = Depends(verify_docs_credentials) if MODE == "DEV" else None):
    if MODE == "PROD":
        raise HTTPException(status_code=404, detail="Not Found")
    return get_openapi(title="FastAPI APP", version="1.0.0", routes=app.routes)

@app.get("/redoc", include_in_schema=False)
def get_redoc():
    raise HTTPException(status_code=404, detail="Not Found")


def get_user_from_db(username: str) -> Optional[UserInDB]:
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    if row:
        return UserInDB(username=row["username"], hashed_password=row["password"], role=row["role"])
    return None


def auth_user_basic(credentials: HTTPBasicCredentials = Depends(security_basic)):
    user = get_user_from_db(credentials.username)

    if not user or not secrets.compare_digest(user.username, credentials.username):
        raise HTTPException(status_code=401, detail="Unauthorized", headers={"WWW-Authenticate": "Basic"})
    
    if not pwd_context.verify(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Unauthorized", headers={"WWW-Authenticate": "Basic"})
    
    return user

@app.get("/login")
def login_basic(user: UserInDB = Depends(auth_user_basic)):
    return {"message": f"Welcome, {user.username}!"}


@app.post("/register", status_code=201)
@limiter.limit("1/minute")
def register_user(request: Request, user: User):
    existing_user = get_user_from_db(user.username)
    if existing_user:
        raise HTTPException(status_code=409, detail="User already exists")
    
    hashed_password = pwd_context.hash(user.password)
    
    role = "user"
    if user.username == "admin":
        role = "admin"
    elif user.username == "guest":
        role = "guest"
        
    conn = get_db_connection()
    conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (user.username, hashed_password, role))
    conn.commit()
    conn.close()
    
    return {"message": "New user created"}

@app.post("/login")
@limiter.limit("5/minute")
def login_jwt(request: Request, user: User):
    db_user = get_user_from_db(user.username)
    
    if not db_user or not secrets.compare_digest(db_user.username, user.username):
        raise HTTPException(status_code=404, detail="User not found")
        
    if not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Authorization failed")
    
    payload = {
        "sub": db_user.username,
        "role": db_user.role,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}


def get_current_user_jwt(credentials: HTTPAuthorizationCredentials = Depends(security_bearer)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        user = get_user_from_db(username)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def role_required(allowed_roles: list):
    def role_checker(user: UserInDB = Depends(get_current_user_jwt)):
        if user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return user
    return role_checker

@app.get("/protected_resource")
def protected_resource(user: UserInDB = Depends(get_current_user_jwt)):
    return {"message": "Access granted", "user": user.username, "role": user.role}

@app.post("/admin/resource")
def admin_resource(user: UserInDB = Depends(role_required(["admin"]))):
    return {"message": "Admin action performed"}

@app.put("/user/resource")
def user_resource(user: UserInDB = Depends(role_required(["admin", "user"]))):
    return {"message": "User action performed"}

@app.get("/guest/resource")
def guest_resource(user: UserInDB = Depends(role_required(["admin", "user", "guest"]))):
    return {"message": "Guest action performed"}


@app.post("/todos", response_model=TodoResponse, status_code=201)
def create_todo(todo: TodoCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO todos (title, description, completed) VALUES (?, ?, ?)",
        (todo.title, todo.description, False)
    )
    todo_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {"id": todo_id, "title": todo.title, "description": todo.description, "completed": False}

@app.get("/todos/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"id": row["id"], "title": row["title"], "description": row["description"], "completed": bool(row["completed"])}

@app.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo: TodoUpdate):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Todo not found")
        
    conn.execute(
        "UPDATE todos SET title = ?, description = ?, completed = ? WHERE id = ?",
        (todo.title, todo.description, todo.completed, todo_id)
    )
    conn.commit()
    conn.close()
    return {"id": todo_id, "title": todo.title, "description": todo.description, "completed": todo.completed}

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Todo not found")
        
    conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    conn.commit()
    conn.close()
    return {"message": "Todo deleted successfully"}