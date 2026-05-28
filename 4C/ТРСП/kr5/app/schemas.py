from pydantic import BaseModel, Field
from typing import Optional


class TaskCreate(BaseModel):
    """Схема для создания задачи"""
    title: str = Field(..., min_length=3, max_length=80, description="Название задачи")
    description: Optional[str] = Field(None, description="Описание задачи")
    status: str = Field(default="todo", description="Статус задачи")
    priority: int = Field(..., ge=1, le=5, description="Приоритет от 1 до 5")


class TaskUpdate(BaseModel):
    """Схема для обновления статуса задачи"""
    status: str = Field(..., description="Новый статус задачи")


class TaskResponse(BaseModel):
    """Схема ответа для задачи"""
    id: int
    title: str
    description: Optional[str] = None
    status: str
    priority: int
    owner_id: int


class User(BaseModel):
    """Схема пользователя"""
    id: int
    role: str


class HealthResponse(BaseModel):
    """Схема ответа для проверки статуса"""
    status: str
    env: Optional[str] = None


class RoomUsersResponse(BaseModel):
    """Схема ответа со списком пользователей в комнате"""
    room_id: str
    users: list[str]


class StatsResponse(BaseModel):
    """Схема ответа со статистикой"""
    total_tasks: int
    by_status: dict[str, int]
