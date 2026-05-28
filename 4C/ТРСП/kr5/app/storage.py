from typing import Dict, List, Set
from fastapi import WebSocket


class Task:
    """Модель задачи для хранения"""
    _id_counter = 0

    def __init__(self, title: str, description: str | None, status: str, priority: int, owner_id: int):
        Task._id_counter += 1
        self.id = Task._id_counter
        self.title = title
        self.description = description
        self.status = status
        self.priority = priority
        self.owner_id = owner_id

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "owner_id": self.owner_id,
        }


class TaskStorage:
    """Хранилище задач в памяти"""
    def __init__(self):
        self.tasks: List[Task] = []

    def clear(self):
        """Очист хранилища"""
        self.tasks.clear()
        Task._id_counter = 0

    def create_task(self, title: str, description: str | None, status: str, priority: int, owner_id: int) -> Task:
        """Создать новую задачу"""
        task = Task(title, description, status, priority, owner_id)
        self.tasks.append(task)
        return task

    def get_task_by_id(self, task_id: int, owner_id: int | None = None) -> Task | None:
        """Получить задачу по ID"""
        for task in self.tasks:
            if task.id == task_id and (owner_id is None or task.owner_id == owner_id):
                return task
        return None

    def get_user_tasks(self, owner_id: int, status: str | None = None, min_priority: int | None = None) -> List[Task]:
        """Получить все задачи пользователя с фильтрацией"""
        result = [task for task in self.tasks if task.owner_id == owner_id]
        
        if status:
            result = [task for task in result if task.status == status]
        
        if min_priority is not None:
            result = [task for task in result if task.priority >= min_priority]
        
        return result

    def update_task_status(self, task_id: int, new_status: str, owner_id: int | None = None) -> Task | None:
        """Обновить статус задачи"""
        task = self.get_task_by_id(task_id, owner_id)
        if task:
            task.status = new_status
            return task
        return None

    def delete_task(self, task_id: int, owner_id: int | None = None) -> bool:
        """Удалить задачу"""
        for i, task in enumerate(self.tasks):
            if task.id == task_id and (owner_id is None or task.owner_id == owner_id):
                self.tasks.pop(i)
                return True
        return False

    def get_all_stats(self) -> dict:
        """Получить статистику по всем задачам"""
        total = len(self.tasks)
        by_status = {"todo": 0, "in_progress": 0, "done": 0}
        for task in self.tasks:
            if task.status in by_status:
                by_status[task.status] += 1
        return {"total_tasks": total, "by_status": by_status}


class RoomManager:
    """Менеджер комнат WebSocket"""
    def __init__(self):
        self.rooms: Dict[str, Dict[str, WebSocket]] = {}

    async def connect(self, room_id: str, username: str, websocket: WebSocket):
        """Подключить пользователя к комнате"""
        if room_id not in self.rooms:
            self.rooms[room_id] = {}
        
        self.rooms[room_id][username] = websocket
        
        # Отправить уведомление о подключении
        await self.broadcast(room_id, {
            "type": "user_joined",
            "username": username,
            "room_id": room_id
        })

    async def disconnect(self, room_id: str, username: str):
        """Отключить пользователя от комнаты"""
        if room_id in self.rooms and username in self.rooms[room_id]:
            del self.rooms[room_id][username]
            
            if not self.rooms[room_id]:
                del self.rooms[room_id]
            else:
                # Отправить уведомление об отключении
                await self.broadcast(room_id, {
                    "type": "user_left",
                    "username": username,
                    "room_id": room_id
                })

    async def broadcast(self, room_id: str, payload: dict):
        """Разослать сообщение всем пользователям комнаты"""
        if room_id in self.rooms:
            disconnected = []
            for username, websocket in self.rooms[room_id].items():
                try:
                    await websocket.send_json(payload)
                except Exception:
                    disconnected.append(username)
            
            # Удалить отключившихся
            for username in disconnected:
                del self.rooms[room_id][username]

    def get_users(self, room_id: str) -> List[str]:
        """Получить список пользователей в комнате"""
        if room_id in self.rooms:
            return list(self.rooms[room_id].keys())
        return []
