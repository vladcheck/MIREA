from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from models import User, UserWithAge, ValidatedFeedback, CalculationRequest
from typing import Any

app: Any = FastAPI()

# Хранилище для отзывов
feedbacks: list[Any] = []


# Task 1.1 - GET / returns JSON welcome message
@app.get("/")
async def read_root() -> dict[str, str]:
    return {"message": "Добро пожаловать в моё приложение FastAPI!"}


# Task 1.3 - POST /calculate - calculator (sum of two numbers)
@app.post("/calculate")
async def calculate(data: CalculationRequest) -> dict[str, float]:
    result = data.num1 + data.num2
    return {"result": result}


# Task 1.4 - GET /users - return user information
@app.get("/users")
async def get_users() -> User:
    user = User(name="Ваше Имя и Фамилия", id=1)
    return user


# Task 1.5 - POST /user - check user age and return with is_adult flag
@app.post("/user")
async def check_user_age(user: UserWithAge) -> dict[str, Any]:
    is_adult: bool = user.age >= 18
    return {"name": user.name, "age": user.age, "is_adult": is_adult}


# Task 2.1 and 2.2 - POST /feedback - submit feedback with validation
@app.post("/feedback")
async def submit_feedback(feedback: ValidatedFeedback) -> dict[str, str]:
    feedbacks.append(feedback.model_dump())
    return {"message": f"Feedback received. Thank you, {feedback.name}."}


# Task 1.2 - GET /html - return HTML file
@app.get("/html", response_class=HTMLResponse)
async def get_html() -> Any:
    return FileResponse("index.html")
