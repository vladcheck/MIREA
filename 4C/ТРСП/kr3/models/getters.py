import jwt
from sqlite3 import Connection, Row
from typing import Optional, Any, Dict

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from db.database import get_db_connection
from const import ALGORITHM, SECRET_KEY, security_bearer
from models.models import UserInDB


def get_user_from_db(username: str) -> Optional[UserInDB]:
    conn: Connection = get_db_connection()
    row: Row = conn.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()
    conn.close()
    if row:
        return UserInDB(
            username=row["username"], hashed_password=row["password"], role=row["role"]
        )
    return None


def get_current_user_jwt(
    credentials: HTTPAuthorizationCredentials = Depends(security_bearer),
) -> UserInDB:
    try:
        payload: Dict[str, Any] = jwt.decode(
            credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM]
        )
        username: str | None = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        user: UserInDB | None = get_user_from_db(username)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
