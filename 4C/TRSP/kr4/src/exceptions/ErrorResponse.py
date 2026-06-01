from pydantic import BaseModel


class ErrorResponse(BaseModel):
    error: str
    code: int
    detail: str
