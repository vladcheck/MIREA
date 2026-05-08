from pydantic import BaseModel, field_validator, Field
from typing import Any
import re


# Task 1.4 - User model for GET /users
class User(BaseModel):
    name: str
    id: int


# Task 1.5 - User model with age for POST /user
class UserWithAge(BaseModel):
    name: str
    age: int


# Task 2.1 - Basic Feedback model
class Feedback(BaseModel):
    name: str
    message: str


# Task 2.2 - Feedback model with validation
class ValidatedFeedback(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    message: str = Field(..., min_length=10, max_length=500)

    @field_validator("message")
    @classmethod
    def validate_forbidden_words(cls, v) -> Any:
        forbidden_words: list[str] = ["кринж", "рофл", "вайб"]
        text_lower: str = v.lower()

        for word in forbidden_words:
            if re.search(rf"\b{re.escape(word)}\w*\b", text_lower):
                raise ValueError("Использование недопустимых слов")

        return v


# Task 1.3 - Calculator request model
class CalculationRequest(BaseModel):
    num1: float
    num2: float
