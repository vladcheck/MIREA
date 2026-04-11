from typing import Dict

from fastapi import Depends

from models.getters import get_current_user_jwt
from models.models import UserInDB
from main import app


@app.get("/protected_resource")
def protected_resource(
    user: UserInDB = Depends(get_current_user_jwt),
) -> Dict[str, str]:
    return {"message": "Access granted", "user": user.username, "role": user.role}


@app.post("/admin/resource")
def admin_resource() -> Dict[str, str]:
    return {"message": "Admin action performed"}


@app.put("/user/resource")
def user_resource() -> Dict[str, str]:
    return {"message": "User action performed"}


@app.get("/guest/resource")
def guest_resource() -> Dict[str, str]:
    return {"message": "Guest action performed"}
