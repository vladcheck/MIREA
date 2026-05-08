import secrets
from fastapi import Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasicCredentials
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from const import MODE, DOCS_USER, DOCS_PASSWORD, security_basic
from main import app
from typing import Dict, Any, NoReturn


def verify_docs_credentials(
    credentials: HTTPBasicCredentials = Depends(security_basic),
) -> str:
    correct_user: bool = secrets.compare_digest(credentials.username, DOCS_USER)
    correct_password: bool = secrets.compare_digest(credentials.password, DOCS_PASSWORD)
    if not (correct_user and correct_password):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get("/docs", include_in_schema=False)
def get_docs() -> HTMLResponse:
    if MODE == "PROD":
        raise HTTPException(status_code=404, detail="Not Found")
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Docs")


@app.get("/openapi.json", include_in_schema=False)
def get_openapi_endpoint() -> Dict[str, Any]:
    if MODE == "PROD":
        raise HTTPException(status_code=404, detail="Not Found")
    return get_openapi(title="FastAPI APP", version="1.0.0", routes=app.routes)


@app.get("/redoc", include_in_schema=False)
def get_redoc() -> NoReturn:
    raise HTTPException(status_code=404, detail="Not Found")
