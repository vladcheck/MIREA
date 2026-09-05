from pydantic import BaseModel


class UserIn(BaseModel):
    username: str
    age: int
