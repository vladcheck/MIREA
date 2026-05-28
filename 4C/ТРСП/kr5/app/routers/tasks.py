from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.schemas import TaskCreate, TaskResponse, TaskUpdate, User
from app.storage import TaskStorage
from app.dependencies import get_current_user, get_storage

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage)
) -> TaskResponse:
    """Создать новую задачу"""
    if len(task_data.title) < 3 or len(task_data.title) > 80:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Title must be between 3 and 80 characters"
        )
    
    task = storage.create_task(
        title=task_data.title,
        description=task_data.description,
        status=task_data.status,
        priority=task_data.priority,
        owner_id=current_user.id
    )
    return TaskResponse(**task.to_dict())


@router.get("", response_model=list[TaskResponse])
async def get_tasks(
    status: str | None = Query(None),
    min_priority: int | None = Query(None),
    current_user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage)
) -> list[TaskResponse]:
    """Получить список задач текущего пользователя"""
    tasks = storage.get_user_tasks(current_user.id, status=status, min_priority=min_priority)
    return [TaskResponse(**task.to_dict()) for task in tasks]


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage)
) -> TaskResponse:
    """Получить одну задачу"""
    task = storage.get_task_by_id(task_id, owner_id=current_user.id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return TaskResponse(**task.to_dict())


@router.patch("/{task_id}/status", response_model=TaskResponse)
async def update_task_status(
    task_id: int,
    update_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage)
) -> TaskResponse:
    """Обновить статус задачи"""
    task = storage.update_task_status(task_id, update_data.status, owner_id=current_user.id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return TaskResponse(**task.to_dict())


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage)
):
    """Удалить задачу"""
    if not storage.delete_task(task_id, owner_id=current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
