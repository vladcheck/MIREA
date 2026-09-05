from typing import Dict

from fastapi import FastAPI, Request
import users
import exceptions

app = FastAPI(title="Control Work 4 API")
app.include_router(users.router)
app.include_router(exceptions.router)


@router.exception_handler(CustomExceptionA)
async def custom_exception_a_handler(_: Request, exc: CustomExceptionA) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            error="Condition Not Met", code=400, detail=f"Invalid name: {exc.name}"
        ).model_dump(),
    )


@app.exception_handler(CustomExceptionB)
async def custom_exception_b_handler(_: Request, exc: CustomExceptionB) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(
            error="Not Found", code=404, detail=f"Resource {exc.resource_id} not found"
        ).model_dump(),
    )


@app.get("/error_a/{name}")
def trigger_error_a(name: str) -> Dict[str, str]:
    if name == "bad":
        raise CustomExceptionA(name=name)
    return {"message": "Success"}


@app.get("/error_b/{resource_id}")
def trigger_error_b(resource_id: int) -> Dict[str, str]:
    if resource_id == 0:
        raise CustomExceptionB(resource_id=resource_id)
    return {"message": "Success"}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error="Validation Error", code=422, detail=str(exc.errors())
        ).model_dump(),
    )


@app.get("/")
async def root() -> Dict[str, str]:
    return {"message": "Hello Bigger Applications!"}


def main() -> None:
    print("Hello from kr4!")


if __name__ == "__main__":
    main()
