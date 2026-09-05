from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserData(BaseModel):
    username: str
    age: int = Field(gt=18)
    email: EmailStr
    password: str = Field(min_length=8, max_length=16)
    phone: Optional[str] = "Unknown"
