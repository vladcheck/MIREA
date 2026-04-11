# Контрольная работа №3

## Особенности реализации
- Настроены хендлеры как для авторизации через Basic Auth (для документации и базового маршрута `/login`), так и POST-эндпоинты (для JWT и регистрации).
- Маршрут POST `/register` ограничен 1 запросом в минуту, а `POST /login` - 5 запросами в минуту. (средствами `slowapi`).
- Используется библиотека `sqlite3` для работы с таблицами `users` и `todos`. (при старте приложения автоматически создастся `database.db`).
- Если установить переменную `MODE=PROD` в `.env`, swagger и redoc будут недоступны. При `MODE=DEV` доступ в Swagger (`/docs`) защищен секретами `DOCS_USER` и `DOCS_PASSWORD`.
- Добавлен разделенный доступ и отдельные эндпоинты по ролям (`admin`, `user`, `guest`).

## Установка и запуск

1. Клонируйте репозиторий и перейдите в папку проекта. 
2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте `.env` файл на основе `.env.example`:
```bash
cp .env.example .env
```

4. Запустите сервер:
```bash
uvicorn main:app --reload
```

## Как тестировать

### Аутентификация 

Регистрация в базе данных (хэшер `bcrypt`):
```bash
curl -X 'POST' 'http://127.0.0.1:8000/register' \
-H 'Content-Type: application/json' \
-d '{"username": "admin", "password": "123"}'
```

Генерация JWT-токена:
```bash
curl -X 'POST' 'http://127.0.0.1:8000/login' \
-H 'Content-Type: application/json' \
-d '{"username": "admin", "password": "123"}'
```

Доступ к ресурсу по JWT токене (токен взять из команды выше):
```bash
curl -X 'GET' 'http://127.0.0.1:8000/protected_resource' \
-H 'Authorization: Bearer <ваш-токен>'
```

### Доступ к документации (Base Auth)

Ознакомиться со всеми эндпоинтами можно в защищенной документации по ссылке `/docs` в браузере:
```bash
curl -u admin:admin http://127.0.0.1:8000/docs
```
*(Если `MODE=PROD`, данная страница выдаст 404)*

### CRUD операции (Todo)

Создать запись `Todo`:
```bash
curl -X 'POST' 'http://127.0.0.1:8000/todos' \
-H 'Content-Type: application/json' \
-d '{"title": "Buy groceries", "description": "Milk, eggs, bread"}'
```

Получить всё о задаче по id:
```bash
curl -X 'GET' 'http://127.0.0.1:8000/todos/1'
```
