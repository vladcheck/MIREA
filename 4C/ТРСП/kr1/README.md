# ТРСП - КР1

## Настройка окружения

```bash
python -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
```

## Запуск

```bash
uvicorn app:app --reload
```

Сервер работает на порту `8000`

## Документаця

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Тесты

### Тест 1.1 - Получить JSON

```bash
curl http://localhost:8000/
```

### Тест 1.2 - Получить HTML

```bash
curl http://localhost:8000/html
```

### Тест 1.3 - Калькулятор

```bash
curl -X POST http://localhost:8000/calculate \
  -H "Content-Type: application/json" \
  -d '{"num1": 5, "num2": 10}'
```

### Тест 1.4 - Получить пользователей

```bash
curl http://localhost:8000/users
```

### Тест 1.5 - Проверить конкретного пользователя на совершеннолетие

```bash
curl -X POST http://localhost:8000/user \
  -H "Content-Type: application/json" \
  -d '{"name": "John", "age": 25}'
```

### Тест 2.1 - Подтвердить фидбек

```bash
curl -X POST http://localhost:8000/feedback \
  -H "Content-Type: application/json" \
  -d '{"name": "John", "message": "Excellent application!"}'
```

### Тест 2.2 - Некорректный фидбек (содержит запрещенное слово)

```bash
curl -X POST http://localhost:8000/feedback \
  -H "Content-Type: application/json" \
  -d '{"name": "John", "message": "полный кринж"}'
```

Ожидается: HTTP 422 with validation error

### Тест 2.3 - Некорректный фидбек (слишком короткое имя)

```bash
curl -X POST http://localhost:8000/feedback \
  -H "Content-Type: application/json" \
  -d '{"name": "J", "message": "This is a valid message"}'
```

Ожидается: HTTP 422 with validation error
