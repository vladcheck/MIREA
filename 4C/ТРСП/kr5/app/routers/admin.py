from fastapi import APIRouter, Depends, status, HTTPException
from app.schemas import StatsResponse, User
from app.storage import TaskStorage
from app.dependencies import require_admin, get_storage

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    current_user: User = Depends(require_admin),
    storage: TaskStorage = Depends(get_storage)
) -> StatsResponse:
    """Получить статистику по всем задачам (только для администраторов)"""
    stats = storage.get_all_stats()
    return StatsResponse(**stats)


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_admin(
    task_id: int,
    current_user: User = Depends(require_admin),
    storage: TaskStorage = Depends(get_storage)
):
    """Удалить любую задачу (только для администраторов)"""
    if not storage.delete_task(task_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
