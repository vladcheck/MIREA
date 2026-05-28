from fastapi import Depends, Header, HTTPException, status
from app.schemas import User
from app.storage import TaskStorage

# Глобальное хранилище
storage = TaskStorage()


async def get_current_user(x_user_id: int | None = Header(None), x_user_role: str = Header("user")) -> User:
    """
    Зависимость для получения текущего пользователя.
    Читает заголовки X-User-Id и X-User-Role.
    """
    if x_user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="X-User-Id header is missing")
    
    try:
        user_id = int(x_user_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="X-User-Id must be an integer")
    
    return User(id=user_id, role=x_user_role)


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Зависимость для проверки, что пользователь администратор.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    return current_user


async def get_storage() -> TaskStorage:
    """
    Зависимость для получения хранилища задач.
    """
    return storage
