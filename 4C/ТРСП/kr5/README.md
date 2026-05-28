# Система управления задачами с WebSocket чатом

Полнофункциональное веб-приложение на FastAPI для управления задачами с поддержкой WebSocket-чата и Docker-контейнеризацией.

## Требования

- Python 3.12 или выше
- Docker и Docker Compose (для контейнеризации)
- pip для управления зависимостями

## Структура проекта

```
app/
  __init__.py              # Пакет приложения
  main.py                  # Главное приложение FastAPI
  schemas.py               # Pydantic схемы
  storage.py               # Модели и хранилище данных
  dependencies.py          # Зависимости и middleware
  routers/
    __init__.py
    tasks.py               # Маршруты для задач
    users.py               # Маршруты для пользователей
    admin.py               # Маршруты администратора
tests/
  __init__.py
  test_tasks.py            # Тесты для API задач
  test_websocket.py        # Тесты для WebSocket
  test_dependencies_and_routing.py  # Тесты зависимостей и маршрутизации
Dockerfile                 # Конфигурация Docker образа
docker-compose.yml         # Конфигурация Docker Compose
requirements.txt           # Зависимости Python
README.md                  # Этот файл
```

## Запуск локально

### 1. Создание виртуального окружения

```bash
python -m venv .venv
```

### 2. Активация виртуального окружения

Windows:
```bash
.venv\Scripts\activate
```

Linux/MacOS:
```bash
source .venv/bin/activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Запуск приложения

```bash
uvicorn app.main:app --reload
```

Приложение будет доступно по адресу: http://localhost:8000

### 5. Запуск тестов

```bash
pytest
```

Для запуска с подробным выводом:
```bash
pytest -v
```

## Запуск в Docker

### 1. Сборка образа и запуск контейнера

```bash
docker compose up --build
```

Приложение будет доступно по адресу: http://localhost:8000

### 2. Остановка контейнера

```bash
docker compose down
```

### 3. Просмотр логов

```bash
docker compose logs -f
```

## API Эндпоинты

### Проверка здоровья приложения

**GET /health**

Проверяет состояние приложения.

Пример запроса:
```bash
curl http://localhost:8000/health
```

Ответ:
```json
{
  "status": "ok",
  "env": "local"
}
```

### Управление задачами

Все маршруты требуют заголовка `X-User-Id`.

#### Создание задачи

**POST /tasks**

Заголовки:
- `X-User-Id: <user_id>` (обязательно)
- `X-User-Role: user` (опционально, по умолчанию "user")

Тело запроса:
```json
{
  "title": "Название задачи",
  "description": "Описание задачи",
  "status": "todo",
  "priority": 4
}
```

Ответ (201 Created):
```json
{
  "id": 1,
  "title": "Название задачи",
  "description": "Описание задачи",
  "status": "todo",
  "priority": 4,
  "owner_id": 10
}
```

#### Получение всех задач пользователя

**GET /tasks**

Параметры запроса:
- `status` (опционально) - фильтр по статусу (todo, in_progress, done)
- `min_priority` (опционально) - минимальный приоритет (1-5)

Пример:
```bash
curl -H "X-User-Id: 10" http://localhost:8000/tasks
curl -H "X-User-Id: 10" "http://localhost:8000/tasks?status=done&min_priority=3"
```

#### Получение одной задачи

**GET /tasks/{task_id}**

```bash
curl -H "X-User-Id: 10" http://localhost:8000/tasks/1
```

#### Изменение статуса задачи

**PATCH /tasks/{task_id}/status**

Тело запроса:
```json
{
  "status": "done"
}
```

```bash
curl -X PATCH -H "X-User-Id: 10" -H "Content-Type: application/json" \
  -d '{"status": "done"}' \
  http://localhost:8000/tasks/1
```

#### Удаление задачи

**DELETE /tasks/{task_id}**

Ответ: 204 No Content

```bash
curl -X DELETE -H "X-User-Id: 10" http://localhost:8000/tasks/1
```

### Маршруты пользователей

#### Получение информации о текущем пользователе

**GET /users/me**

```bash
curl -H "X-User-Id: 10" -H "X-User-Role: admin" http://localhost:8000/users/me
```

Ответ:
```json
{
  "id": 10,
  "role": "admin"
}
```

#### Получение информации о пользователе

**GET /users/{user_id}**

```bash
curl http://localhost:8000/users/1
```

### Маршруты администратора

Все маршруты требуют заголовка `X-User-Role: admin`.

#### Получение статистики

**GET /admin/stats**

```bash
curl -H "X-User-Id: 10" -H "X-User-Role: admin" http://localhost:8000/admin/stats
```

Ответ:
```json
{
  "total_tasks": 5,
  "by_status": {
    "todo": 2,
    "in_progress": 1,
    "done": 2
  }
}
```

#### Удаление задачи администратором

**DELETE /admin/tasks/{task_id}**

Администратор может удалить задачу любого пользователя.

```bash
curl -X DELETE -H "X-User-Id: 1" -H "X-User-Role: admin" http://localhost:8000/admin/tasks/1
```

### WebSocket чат

#### Подключение к комнате

**WebSocket /ws/rooms/{room_id}?username={username}**

Пример подключения с помощью websocat:
```bash
websocat ws://localhost:8000/ws/rooms/python?username=alice
```

#### События WebSocket

После подключения вы будете получать события в формате JSON:

**Событие подключения**
```json
{
  "type": "user_joined",
  "room_id": "python",
  "username": "alice"
}
```

**Отправка сообщения**
```json
{
  "type": "message",
  "text": "Привет, всем!"
}
```

**Получение сообщения**
```json
{
  "type": "message",
  "room_id": "python",
  "username": "alice",
  "text": "Привет, всем!"
}
```

**Ошибка при слишком длинном сообщении**
```json
{
  "type": "error",
  "detail": "Message is too long"
}
```

**Событие отключения пользователя**
```json
{
  "type": "user_left",
  "room_id": "python",
  "username": "alice"
}
```

#### Получение списка пользователей в комнате

**GET /rooms/{room_id}/users**

```bash
curl http://localhost:8000/rooms/python/users
```

Ответ:
```json
{
  "room_id": "python",
  "users": ["alice", "bob"]
}
```

## Документация Swagger UI

После запуска приложения документация Swagger UI доступна по адресу:

```
http://localhost:8000/docs
```

## Тестирование

### Запуск всех тестов

```bash
pytest
```

### Запуск тестов конкретного файла

```bash
pytest tests/test_tasks.py -v
pytest tests/test_websocket.py -v
pytest tests/test_dependencies_and_routing.py -v
```

### Запуск тестов с покрытием кода

```bash
pytest --cov=app tests/
```

## Ошибки и их коды

- **400 Bad Request** - неверные данные запроса
- **401 Unauthorized** - отсутствует или некорректна авторизация
- **403 Forbidden** - недостаточно прав доступа
- **404 Not Found** - задача или ресурс не найден
- **422 Unprocessable Entity** - ошибка валидации данных

## Переменные окружения

- `APP_ENV` - окружение приложения (local, docker)

## Управление версиями

Проект использует git для управления версиями. Для сохранения работы выполните:

```bash
git add .
git commit -m "Описание изменений"
git push
```
