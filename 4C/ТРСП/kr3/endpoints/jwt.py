from datetime import datetime, timedelta
from typing import Any, Dict

import jwt

from const import ALGORITHM, SECRET_KEY
from models.models import UserInDB

type Payload = Dict[str, Any]


def encode_jwt_token(db_user: UserInDB) -> str:
    payload: Payload = build_user_payload(db_user)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def build_user_payload(db_user: UserInDB) -> Payload:
    return {
        "sub": db_user.username,
        "role": db_user.role,
        "exp": datetime.utcnow() + timedelta(hours=1),
    }
