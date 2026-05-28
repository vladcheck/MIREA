from fastapi import APIRouter, Depends
from app.schemas import User
from app.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)) -> User:
    """Получить информацию о текущем пользователе"""
    return current_user


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: int) -> User:
    """Получить информацию о пользователе по ID"""
    return User(id=user_id, role="user")
