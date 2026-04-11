from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    username: str

class User(UserBase):
    password: str

class UserInDB(UserBase):
    hashed_password: str
    role: str = "user"

class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    
class TodoUpdate(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool

class TodoResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    completed: bool