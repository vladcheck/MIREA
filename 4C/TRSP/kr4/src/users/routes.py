from _thread import lock
from itertools import count
from threading import Lock
from typing import Any, Dict

from fastapi import HTTPException, Response

from users.UserData import UserData
from users.UserIn import UserIn
from users.UserOut import UserOut
from fastapi import APIRouter
from db import db

router = APIRouter()

_id_seq: count[int] = count(start=1)
_id_lock: lock = Lock()


def next_user_id() -> int:
    with _id_lock:
        return next(_id_seq)


@router.post("/validate_user")
def validate_user(user: UserData) -> Dict[str, Any]:
    return {"message": "User validation successful", "user": user.model_dump()}


@router.post("/users", response_model=UserOut, status_code=201)
def create_user(user: UserIn) -> Dict[str, int]:
    user_id: int = next_user_id()
    db[user_id] = user.model_dump()
    return {"id": user_id, **db[user_id]}


@router.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int) -> Dict[str, int]:
    if user_id not in db:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user_id, **db[user_id]}


@router.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int) -> Response:
    if db.pop(user_id, None) is None:
        raise HTTPException(status_code=404, detail="User not found")
    return Response(status_code=204)
