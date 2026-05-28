import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, status, Query, Depends
from fastapi.responses import JSONResponse
from app.schemas import HealthResponse, RoomUsersResponse
from app.storage import RoomManager, TaskStorage
from app.dependencies import get_storage
from app.routers import tasks, users, admin

app = FastAPI(title="Task Management API", version="1.0.0")

# Инициализация менеджера комнат
room_manager = RoomManager()

# Подключить маршруты
app.include_router(tasks.router)
app.include_router(users.router)
app.include_router(admin.router)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Проверить состояние приложения"""
    env = os.getenv("APP_ENV", "local")
    return HealthResponse(status="ok", env=env)


@app.get("/rooms/{room_id}/users", response_model=RoomUsersResponse)
async def get_room_users(room_id: str):
    """Получить список активных пользователей в комнате"""
    users_list = room_manager.get_users(room_id)
    return RoomUsersResponse(room_id=room_id, users=users_list)


@app.websocket("/ws/rooms/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, username: str = Query(...)):
    """WebSocket эндпоинт для чата в комнате"""
    
    # Валидация username
    if not username or not username.strip():
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Username cannot be empty")
        return
    
    username = username.strip()
    
    # Принять соединение
    await websocket.accept()
    
    # Подключить пользователя к комнате
    await room_manager.connect(room_id, username, websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "message":
                text = data.get("text", "")
                
                # Проверка длины сообщения
                if len(text) > 300:
                    await websocket.send_json({
                        "type": "error",
                        "detail": "Message is too long"
                    })
                    continue
                
                # Разослать сообщение всем пользователям комнаты
                await room_manager.broadcast(room_id, {
                    "type": "message",
                    "room_id": room_id,
                    "username": username,
                    "text": text
                })
    
    except WebSocketDisconnect:
        await room_manager.disconnect(room_id, username)
    except Exception as e:
        await room_manager.disconnect(room_id, username)
        raise


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Обработчик общих исключений"""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
