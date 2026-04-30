from itertools import count
from threading import Lock
from typing import Any

from fastapi import HTTPException, APIRouter,Response
from pydantic import BaseModel

_id_seq = count(start=1)
_id_lock: Lock = Lock()
db: dict[int, dict] = {}
user_router = APIRouter()


def next_user_id() -> int:
    with _id_lock:
        return next(_id_seq)

class UserIn(BaseModel):
    username: str
    age: int

class UserOut(BaseModel):
    id: int
    username: str
    age: int

@user_router.get("/users")
def get_all_users() -> dict[Any, Any]:
    return db

@user_router.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int) -> dict[Any, Any]:
    if user_id not in db:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user_id, **db[user_id]}

@user_router.post("/users", response_model=UserOut, status_code=201)
def create_user(user: UserIn) -> dict[Any, Any]:
    user_id: int = next_user_id()
    db[user_id] = user.model_dump()
    return {"id": user_id, **db[user_id]}

@user_router.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int) -> Response:
    if db.pop(user_id, None) is None:
        raise HTTPException(status_code=404, detail="User not found")
    return Response(status_code=204)