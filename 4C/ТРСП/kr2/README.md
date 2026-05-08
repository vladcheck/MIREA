# Контрольная работа №2 — FastAPI

## Стек

- Python 3.14+
- FastAPI
- Pydantic (валидация данных)
- Uvicorn (ASGI-сервер)
- itsdangerous (подпись cookie)
- Postman (тестирование)

## Как запустить

Ставим зависимости:

```bash
pip install -r requirements.txt
```

Запускаем сервер:

```bash
python app.py
```

Или через uvicorn:

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Документация API будет доступна по адресу <http://localhost:8000/docs>

## Маршруты

### Аутентификация

| Метод | Маршрут | Описание                                                  |
|-------|---------|-----------------------------------------------------------|
| POST  | /login  | Вход в систему, устанавливает cookie session_token        |
| POST  | /logout | Выход из системы, удаляет cookie                          |
| GET   | /user   | Получить профиль текущего пользователя (требуется cookie) |

### Пользователи

| Метод | Маршрут      | Описание             |
|-------|--------------|----------------------|
| POST  | /create_user | Создать пользователя |

### Продукты

| Метод | Маршрут               | Описание                           |
|-------|-----------------------|------------------------------------|
| GET   | /product/{product_id} | Получить продукт по ID             |
| GET   | /products/search      | Поиск продуктов по ключевому слову |

### Системные

| Метод | Маршрут | Описание                   |
|-------|---------|----------------------------|
| GET   | /health | Проверка работоспособности |
| GET   | /       | Информация об API          |

## Тестовые учётные данные

| Username | Password    |
|----------|-------------|
| user123  | password123 |
| admin    | admin123    |
| alice    | alice123    |

## Как запускать тесты в Postman

1. Импортируйте окружение `postman_environment.json` в Postman (Settings → Import)

2. Импортируйте запросы из папок:
   - 01_Task_3.1 — тесты создания пользователя
   - 02_Task_3.2 — тесты продуктов
   - 03_Task_5.1 — тесты cookie-аутентификации
   - 04_Task_5.2 — тесты подписанных cookie
   - 05_Task_5.3 — тесты времени жизни сессии
   - 06_Task_5.4 — тесты заголовков
   - 07_Task_5.5 — тесты CommonHeaders модели

3. Выберите импортированное окружение в правом верхнем углу Postman

4. Откройте Collection Runner (Ctrl+Alt+R или Cmd+Opt+R)

5. Выберите коллекцию и нажмите Run

## Примеры запросов

### Вход в систему

```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user123","password":"password123"}' \
  -c cookies.txt
```

### Получение профиля (с cookie)

```bash
curl http://localhost:8000/user -b cookies.txt
```

### Поиск продуктов

```bash
curl "http://localhost:8000/products/search?keyword=phone&category=Electronics"
```

### Заголовки

```bash
curl http://localhost:8000/headers \
  -H "User-Agent: Mozilla/5.0" \
  -H "Accept-Language: en-US,en;q=0.9"
```

## Структура проекта

```sh
kr-2/
├── app.py           # Основные маршруты
├── models.py        # Pydantic модели
├── auth.py          # Логика аутентификации
├── requirements.txt # Зависимости
└── test/            # Postman коллекции и тесты
```
