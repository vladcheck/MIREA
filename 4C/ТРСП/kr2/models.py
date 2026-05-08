from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from typing import Optional, List
import re


# =============================================================================
# Модели пользователя (Задание 3.1 + 3.2)
# =============================================================================


class UserCreate(BaseModel):
    """
    Модель для создания пользователя с валидацией данных.
    """

    name: str = Field(..., min_length=1, description="Имя пользователя (обязательно)")
    email: EmailStr = Field(
        ..., description="Email адрес (обязательно, валидный формат)"
    )
    age: Optional[int] = Field(
        None, ge=1, le=150, description="Возраст (необязательно, 1-150)"
    )
    is_subscribed: Optional[bool] = Field(
        False, description="Подписка на рассылку (необязательно)"
    )

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Имя не может быть пустым")
        return v.strip()


class UserResponse(BaseModel):
    """
    Модель ответа с данными пользователя.
    """

    name: str
    email: str
    age: Optional[int] = None
    is_subscribed: bool = False

    model_config: ConfigDict = {
        "json_schema_extra": {
            "example": {
                "name": "Alice",
                "email": "alice@example.com",
                "age": 30,
                "is_subscribed": True,
            }
        }
    }


# =============================================================================
# Модели аутентификации (Задание 5.1, 5.2, 5.3)
# =============================================================================


class LoginRequest(BaseModel):
    """
    Модель запроса для входа в систему.
    """

    username: str = Field(..., min_length=1, description="Имя пользователя")
    password: str = Field(..., min_length=1, description="Пароль")

    model_config: ConfigDict = {
        "json_schema_extra": {
            "example": {"username": "user123", "password": "password123"}
        }
    }


class UserProfile(BaseModel):
    """
    Модель профиля пользователя для ответа.
    """

    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    is_authenticated: bool = True
    session_created_at: Optional[str] = None
    last_activity: Optional[str] = None

    model_config: ConfigDict = {
        "json_schema_extra": {
            "example": {
                "username": "user123",
                "email": "user123@example.com",
                "full_name": "User One Two Three",
                "is_authenticated": True,
                "session_created_at": "2026-03-04T12:00:00",
                "last_activity": "2026-03-04T12:05:00",
            }
        }
    }


class LoginResponse(BaseModel):
    """
    Модель ответа после успешного входа.
    """

    message: str
    username: str
    session_token: str

    model_config: ConfigDict = {
        "json_schema_extra": {
            "example": {
                "message": "Успешный вход",
                "username": "user123",
                "session_token": "abc123xyz456",
            }
        }
    }


class ErrorResponse(BaseModel):
    """
    Модель ответа при ошибке.
    """

    message: str
    detail: Optional[str] = None

    model_config: ConfigDict = {
        "json_schema_extra": {
            "example": {"message": "Unauthorized", "detail": "Неверные учётные данные"}
        }
    }


# =============================================================================
# Модели продукта (Задание 3.2)
# =============================================================================


class Product(BaseModel):
    """
    Модель продукта.
    """

    product_id: int = Field(..., description="Уникальный идентификатор продукта")
    name: str = Field(..., description="Название продукта")
    category: str = Field(..., description="Категория продукта")
    price: float = Field(..., ge=0, description="Цена продукта")

    model_config: ConfigDict = {
        "json_schema_extra": {
            "example": {
                "product_id": 123,
                "name": "Smartphone",
                "category": "Electronics",
                "price": 599.99,
            }
        }
    }


class ProductSearchResponse(BaseModel):
    """
    Модель ответа для поиска продуктов.
    """

    products: List[Product]
    total: int = Field(..., description="Общее количество найденных продуктов")
    keyword: str
    category: Optional[str] = None
    limit: int

    model_config: ConfigDict = {
        "json_schema_extra": {
            "example": {
                "products": [
                    {
                        "product_id": 123,
                        "name": "Smartphone",
                        "category": "Electronics",
                        "price": 599.99,
                    }
                ],
                "total": 1,
                "keyword": "phone",
                "category": "Electronics",
                "limit": 5,
            }
        }
    }


# =============================================================================
# Модели заголовков (Задание 5.4, 5.5)
# =============================================================================


class CommonHeaders(BaseModel):
    """
    Модель для извлечения и валидации общих HTTP заголовков.
    Используется в заданиях 5.4 и 5.5.
    """

    user_agent: str = Field(..., description="User-Agent заголовок")
    accept_language: str = Field(..., description="Accept-Language заголовок")

    @field_validator("accept_language")
    @classmethod
    def validate_accept_language(cls, v: str) -> str:
        """
        Валидация формата Accept-Language заголовка.
        Пример правильного формата: "en-US,en;q=0.9,es;q=0.8"
        """
        # Паттерн для валидации Accept-Language
        # Состоит из языковых тегов с необязательными параметрами качества (q)
        pattern = r"^[a-zA-Z]{1,8}(-[a-zA-Z0-9]{1,8})*(\s*,\s*[a-zA-Z]{1,8}(-[a-zA-Z0-9]{1,8})*(\s*;\s*q\s*=\s*[0-9](\.[0-9]{0,3})?)?)*$"

        if not re.match(pattern, v.strip()):
            raise ValueError(
                "Неверный формат Accept-Language. "
                "Пример правильного формата: 'en-US,en;q=0.9,es;q=0.8'"
            )
        return v.strip()

    model_config: ConfigDict = {
        "json_schema_extra": {
            "example": {
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "accept_language": "en-US,en;q=0.9,es;q=0.8",
            }
        }
    }


class HeadersResponse(BaseModel):
    """
    Модель ответа для эндпоинта /headers (Задание 5.4).
    """

    user_agent: str
    accept_language: str

    model_config: ConfigDict = {
        "json_schema_extra": {
            "example": {
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "accept_language": "en-US,en;q=0.9,es;q=0.8",
            }
        }
    }


class InfoResponse(BaseModel):
    """
    Модель ответа для эндпоинта /info (Задание 5.5).
    """

    message: str
    headers: dict

    model_config: ConfigDict = {
        "json_schema_extra": {
            "example": {
                "message": "Добро пожаловать! Ваши заголовки успешно обработаны.",
                "headers": {
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                    "accept_language": "en-US,en;q=0.9,es;q=0.8",
                },
            }
        }
    }
