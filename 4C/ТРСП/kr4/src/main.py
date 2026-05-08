from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .exceptions import CustomExceptionA, CustomExceptionB
from .models.user.model import UserData
from .models.user.routes import user_router

app = FastAPI(title="Control Work 4 API")
app.include_router(user_router)
db: dict[int, dict] = {}

class ErrorResponse(BaseModel):
    error: str
    code: int
    detail: str

@app.exception_handler(CustomExceptionA)
async def custom_exception_a_handler(request: Request, exc: CustomExceptionA) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(error="Condition Not Met", code=400, detail=f"Invalid name: {exc.name}").model_dump()
    )

@app.exception_handler(CustomExceptionB)
async def custom_exception_b_handler(request: Request, exc: CustomExceptionB):
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(error="Not Found", code=404, detail=f"Resource {exc.resource_id} not found").model_dump()
    )

@app.get("/error_a/{name}")
def trigger_error_a(name: str):
    if name == "bad":
        raise CustomExceptionA(name=name)
    return {"message": "Success"}

@app.get("/error_b/{resource_id}")
def trigger_error_b(resource_id: int):
    if resource_id == 0:
        raise CustomExceptionB(resource_id=resource_id)
    return {"message": "Success"}

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(error="Validation Error", code=422, detail=str(exc.errors())).model_dump()
    )

@app.post("/validate_user")
def validate_user(user: UserData)-> dict[str, Any]:
    return {"message": "User validation successful", "user": user.model_dump()}



