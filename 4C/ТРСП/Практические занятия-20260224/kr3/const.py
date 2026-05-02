import os

from fastapi.security import HTTPBasic, HTTPBearer
from passlib.context import CryptContext

MODE: str = os.getenv("MODE", "DEV")
if MODE not in ["DEV", "PROD"]:
    raise ValueError(f"Invalid MODE: {MODE}. Must be 'DEV' or 'PROD'.")

DOCS_USER: str = os.getenv("DOCS_USER", "admin")
DOCS_PASSWORD: str = os.getenv("DOCS_PASSWORD", "admin")
SECRET_KEY: str = os.getenv("SECRET_KEY", "secret_key")
ALGORITHM: str = "HS256"

security_basic = HTTPBasic()
security_bearer = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
