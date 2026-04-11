import secrets

from const import pwd_context
from fastapi.security import HTTPBasicCredentials
from models.models import User, UserInDB


def do_usernames_match(user: UserInDB, credentials: HTTPBasicCredentials) -> bool:
    return secrets.compare_digest(user.username, credentials.username)


def do_users_match(db_user: UserInDB, user: User) -> bool:
    return secrets.compare_digest(db_user.username, user.username)


def is_password_valid(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
