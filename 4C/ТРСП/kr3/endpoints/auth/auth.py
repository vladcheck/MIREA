from sqlite3 import Connection, Row
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBasicCredentials
from typing import Dict

from endpoints.jwt import encode_jwt_token
from main import app, limiter
from const import security_basic, pwd_context
from validators import *
from db.database import get_db_connection
from models.getters import get_user_from_db
from models.models import User, UserInDB


def auth_user_basic(
    credentials: HTTPBasicCredentials = Depends(security_basic),
) -> UserInDB:
    user: UserInDB | None = get_user_from_db(credentials.username)

    if (
        not user
        or not do_usernames_match(user, credentials)
        or not is_password_valid(credentials.password, user.hashed_password)
    ):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Basic"},
        )

    return user


@app.get("/login")
def login_basic(user: UserInDB = Depends(auth_user_basic)) -> Dict[str, str]:
    return {"message": f"Welcome, {user.username}!"}


@app.post("/register", status_code=201)
@limiter.limit("1/minute")
def register_user(_: Request, user: User) -> Dict[str, str]:
    existing_user: UserInDB | None = get_user_from_db(user.username)
    if existing_user:
        raise HTTPException(status_code=409, detail="User already exists")

    hashed_password: str = pwd_context.hash(user.password)
    role: str = get_role(user.username)

    conn: Connection = get_db_connection()
    conn.execute(
        "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
        (user.username, hashed_password, role),
    )
    conn.commit()
    conn.close()

    return {"message": "New user created"}


def get_role(username: str) -> str:
    conn: Connection = get_db_connection()
    row: Row = conn.execute(
        "SELECT role FROM users WHERE username = ?", (username,)
    ).fetchone()
    conn.close()
    return row["role"] if row else "user"


@app.post("/login")
@limiter.limit("5/minute")
def login_jwt(_: Request, user: User) -> Dict[str, str]:
    db_user: UserInDB | None = get_user_from_db(user.username)

    if not db_user or not do_users_match(db_user, user):
        raise HTTPException(status_code=404, detail="User not found")

    if not is_password_valid(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Authorization failed")

    token: str = encode_jwt_token(db_user)
    return {"access_token": token, "token_type": "bearer"}
