from fastapi import FastAPI, HTTPException, Query, Cookie, Response, Request, Header
from fastapi.responses import JSONResponse
from typing import Optional, List, Annotated
from datetime import datetime
from models import (
    UserCreate,
    UserResponse,
    LoginRequest,
    UserProfile,
    LoginResponse,
    ErrorResponse,
    Product,
    ProductSearchResponse,
    CommonHeaders,
    HeadersResponse,
    InfoResponse,
)
from auth import session_manager

# =============================================================================
# Инициализация приложения
# =============================================================================

app = FastAPI(
    title="User & Product API with Auth",
    description="API для работы с пользователями, продуктами и аутентификацией (Задания 3.1 + 3.2 + 5.1-5.5)",
    version="1.0.0",
)


# =============================================================================
# Пример данных продуктов (Задание 3.2)
# =============================================================================

SAMPLE_PRODUCTS: List[Product] = [
    Product(product_id=123, name="Smartphone", category="Electronics", price=599.99),
    Product(product_id=456, name="Phone Case", category="Accessories", price=19.99),
    Product(product_id=789, name="Iphone", category="Electronics", price=1299.99),
    Product(product_id=101, name="Headphones", category="Accessories", price=99.99),
    Product(product_id=202, name="Smartwatch", category="Electronics", price=299.99),
]


# =============================================================================
# Helper функции
# =============================================================================


def create_unauthorized_response(message: str = "Unauthorized") -> JSONResponse:
    """Создание ответа 401 Unauthorized."""
    return JSONResponse(
        status_code=401,
        content={"message": message},
    )


def create_bad_request_response(detail: str) -> JSONResponse:
    """Создание ответа 400 Bad Request."""
    return JSONResponse(
        status_code=400,
        content={"message": "Bad Request", "detail": detail},
    )


# =============================================================================
# Эндпоинты аутентификации (Задания 5.1, 5.2, 5.3)
# =============================================================================


@app.post(
    "/login",
    response_model=LoginResponse,
    summary="Вход в систему",
    description="Аутентификация пользователя и установка подписанного cookie сессии (Задания 5.1, 5.2, 5.3)",
    tags=["Authentication"],
)
async def login(login_data: LoginRequest, response: Response) -> LoginResponse:
    """
    Вход в систему (Задания 5.1, 5.2, 5.3).

    - **username**: Имя пользователя
    - **password**: Пароль

    При успешном входе устанавливается подписанный cookie "session_token"
    с временем жизни 5 минут (Задание 5.3).
    """
    result = session_manager.authenticate(
        username=login_data.username,
        password=login_data.password,
    )

    if not result:
        raise HTTPException(status_code=401, detail="Неверные учётные данные")

    user_id, token = result

    # Установка cookie сессии (Задание 5.3)
    response.set_cookie(
        key="session_token",
        value=token,
        max_age=300,  # 5 минут (Задание 5.3)
        httponly=True,  # Защита от XSS
        secure=False,  # В production установить True (требуется HTTPS)
        samesite="lax",  # Защита от CSRF
        path="/",
    )

    return LoginResponse(
        message="Успешный вход",
        username=login_data.username,
        session_token=token,
    )


@app.post(
    "/logout",
    summary="Выход из системы",
    description="Удаление сессии и очистка cookie",
    tags=["Authentication"],
)
async def logout(
    response: Response,
    session_token: Optional[str] = Cookie(None),
) -> dict:
    """
    Выход из системы.

    Удаляет сессию и очищает cookie.
    """
    if session_token:
        payload = session_manager.verify_token(session_token)
        if payload:
            user_id = payload.get("user_id")
            if user_id:
                session_manager.invalidate_session(user_id)

    # Очистка cookie
    response.delete_cookie(key="session_token", path="/")

    return {"message": "Успешный выход"}


@app.get(
    "/user",
    response_model=UserProfile,
    summary="Получить профиль пользователя",
    description="Возвращает профиль текущего аутентифицированного пользователя (Задания 5.1, 5.2, 5.3)",
    tags=["Authentication"],
)
async def get_user_profile(
    response: Response,
    session_token: Optional[str] = Cookie(None),
) -> UserProfile:
    """
    Получение профиля текущего пользователя (Задания 5.1, 5.2, 5.3).

    Требует валидный подписанный cookie "session_token".
    Возвращает 401 если токен отсутствует, невалиден или истёк.

    Задание 5.3: Сессия автоматически продлевается при активности.
    """
    if not session_token:
        raise HTTPException(status_code=401, detail={"message": "Unauthorized"})

    # Верификация токена
    payload = session_manager.verify_token(session_token, max_age=300)
    if not payload:
        raise HTTPException(status_code=401, detail={"message": "Session expired"})

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail={"message": "Invalid session"})

    session = session_manager.get_session(session_token)
    if not session:
        raise HTTPException(status_code=401, detail={"message": "Unauthorized"})

    # Задание 5.3: Продление сессии при активности
    if session.should_extend():
        session.extend()
        # Обновляем cookie с новым токеном
        new_timestamp = int(datetime.now().timestamp())
        new_token = session_manager.generate_token(user_id, new_timestamp)
        response.set_cookie(
            key="session_token",
            value=new_token,
            max_age=300,
            httponly=True,
            secure=False,
            samesite="lax",
            path="/",
        )

    return UserProfile(
        username=session.username,
        email=session.email,
        full_name=session.full_name,
        is_authenticated=True,
        session_created_at=session.created_at.isoformat(),
        last_activity=session.last_activity.isoformat(),
    )


@app.get(
    "/profile",
    response_model=UserProfile,
    summary="Получить профиль (альтернативный эндпоинт)",
    description="Альтернативный эндпоинт для получения профиля (Задание 5.3)",
    tags=["Authentication"],
)
async def get_profile(
    response: Response,
    session_token: Optional[str] = Cookie(None),
) -> UserProfile:
    """
    Альтернативный эндпоинт для получения профиля (Задание 5.3).

    Реализует динамическое продление сессии.
    """
    if not session_token:
        raise HTTPException(status_code=401, detail={"message": "Unauthorized"})

    payload = session_manager.verify_token(session_token, max_age=300)
    if not payload:
        raise HTTPException(status_code=401, detail={"message": "Session expired"})

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail={"message": "Invalid session"})

    session = session_manager.get_session(session_token)
    if not session:
        raise HTTPException(status_code=401, detail={"message": "Unauthorized"})

    # Продление сессии
    if session.should_extend():
        session.extend()
        new_timestamp = int(datetime.now().timestamp())
        new_token = session_manager.generate_token(user_id, new_timestamp)
        response.set_cookie(
            key="session_token",
            value=new_token,
            max_age=300,
            httponly=True,
            secure=False,
            samesite="lax",
            path="/",
        )

    return UserProfile(
        username=session.username,
        email=session.email,
        full_name=session.full_name,
        is_authenticated=True,
        session_created_at=session.created_at.isoformat(),
        last_activity=session.last_activity.isoformat(),
    )


# =============================================================================
# Эндпоинты пользователя (Задание 3.1 + 3.2)
# =============================================================================


@app.post(
    "/create_user",
    response_model=UserResponse,
    summary="Создать пользователя",
    description="Принимает POST-запрос с данными пользователя и возвращает их обратно",
    tags=["Users"],
)
async def create_user(user: UserCreate) -> UserResponse:
    """
    Эндпоинт для приёма данных пользователя.
    """
    return UserResponse(
        name=user.name,
        email=user.email,
        age=user.age,
        is_subscribed=user.is_subscribed or False,
    )


# =============================================================================
# Эндпоинты продукта (Задание 3.2)
# =============================================================================


@app.get(
    "/products/search",
    response_model=ProductSearchResponse,
    summary="Поиск продуктов",
    description="Поиск продуктов по ключевому слову с опциональной фильтрацией по категории",
    tags=["Products"],
)
async def search_products(
    keyword: str = Query(
        ..., min_length=1, description="Ключевое слово для поиска (обязательно)"
    ),
    category: Optional[str] = Query(
        None, description="Категория для фильтрации (необязательно)"
    ),
    limit: int = Query(
        10,
        ge=1,
        le=100,
        description="Максимальное количество результатов (по умолчанию 10)",
    ),
) -> ProductSearchResponse:
    """
    Поиск продуктов по ключевому слову.
    """
    # Фильтрация по ключевому слову (регистронезависимый поиск)
    filtered_products = [
        p for p in SAMPLE_PRODUCTS if keyword.lower() in p.name.lower()
    ]

    # Дополнительная фильтрация по категории
    if category:
        filtered_products = [
            p for p in filtered_products if p.category.lower() == category.lower()
        ]

    # Ограничение количества результатов
    result_products = filtered_products[:limit]

    return ProductSearchResponse(
        products=result_products,
        total=len(result_products),
        keyword=keyword,
        category=category,
        limit=limit,
    )


@app.get(
    "/product/{product_id}",
    response_model=Product,
    summary="Получить продукт по ID",
    description="Возвращает информацию о продукте по его идентификатору",
    tags=["Products"],
)
async def get_product(product_id: int) -> Product:
    """
    Получение продукта по идентификатору.
    """
    for product in SAMPLE_PRODUCTS:
        if product.product_id == product_id:
            return product

    raise HTTPException(status_code=404, detail=f"Продукт с ID {product_id} не найден")


# =============================================================================
# Эндпоинты заголовков (Задания 5.4, 5.5)
# =============================================================================


@app.get(
    "/headers",
    response_model=HeadersResponse,
    summary="Получить заголовки запроса",
    description="Извлекает и возвращает заголовки User-Agent и Accept-Language (Задание 5.4)",
    tags=["Headers"],
)
async def get_headers(
    user_agent: Annotated[Optional[str], Header()] = None,
    accept_language: Annotated[Optional[str], Header()] = None,
) -> HeadersResponse:
    """
    Эндпоинт для получения заголовков запроса (Задание 5.4).

    - **User-Agent**: Строка пользовательского агента (обязательно)
    - **Accept-Language**: Предпочтительный язык клиента (обязательно)

    Возвращает 400 если заголовки отсутствуют.
    """
    if not user_agent:
        raise HTTPException(
            status_code=400,
            detail="Заголовок User-Agent обязателен",
        )

    if not accept_language:
        raise HTTPException(
            status_code=400,
            detail="Заголовок Accept-Language обязателен",
        )

    # Валидация формата Accept-Language
    try:
        CommonHeaders(user_agent=user_agent, accept_language=accept_language)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return HeadersResponse(
        user_agent=user_agent,
        accept_language=accept_language,
    )


@app.get(
    "/info",
    response_model=InfoResponse,
    summary="Получить информацию с заголовками",
    description="Возвращает заголовки и приветственное сообщение с кастомным заголовком ответа (Задание 5.5)",
    tags=["Headers"],
)
async def get_info(
    response: Response,
    user_agent: Annotated[Optional[str], Header()] = None,
    accept_language: Annotated[Optional[str], Header()] = None,
) -> InfoResponse:
    """
    Эндпоинт для получения информации с заголовками (Задание 5.5).

    - Использует модель CommonHeaders для валидации (DRY принцип)
    - Добавляет кастомный заголовок ответа X-Server-Time

    Возвращает 400 если заголовки отсутствуют или невалидны.
    """
    if not user_agent:
        raise HTTPException(
            status_code=400,
            detail="Заголовок User-Agent обязателен",
        )

    if not accept_language:
        raise HTTPException(
            status_code=400,
            detail="Заголовок Accept-Language обязателен",
        )

    # Валидация через CommonHeaders (Задание 5.5 - DRY принцип)
    try:
        headers_model = CommonHeaders(
            user_agent=user_agent, accept_language=accept_language
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Добавление кастомного заголовка ответа (Задание 5.5)
    current_time = datetime.now().isoformat()
    response.headers["X-Server-Time"] = current_time

    return InfoResponse(
        message="Добро пожаловать! Ваши заголовки успешно обработаны.",
        headers={
            "user_agent": headers_model.user_agent,
            "accept_language": headers_model.accept_language,
        },
    )


# =============================================================================
# Эндпоинты здоровья и информации
# =============================================================================


@app.get("/health", tags=["System"])
async def health_check():
    """Проверка работоспособности API"""
    return {"status": "ok", "service": "User & Product API with Auth"}


@app.get("/", tags=["System"])
async def root():
    """Корневой эндпоинт с информацией об API"""
    return {
        "message": "Добро пожаловать в User & Product API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "authentication": {
                "login": "POST /login",
                "logout": "POST /logout",
                "profile": "GET /user",
                "profile_alt": "GET /profile",
            },
            "users": "POST /create_user",
            "products": {
                "get": "GET /product/{product_id}",
                "search": "GET /products/search",
            },
            "headers": {
                "get_headers": "GET /headers",
                "get_info": "GET /info",
            },
        },
        "tasks_completed": [
            "3.1 - User POST endpoint",
            "3.2 - Product endpoints",
            "5.1 - Cookie authentication",
            "5.2 - Signed cookie with itsdangerous",
            "5.3 - Dynamic session lifetime (5 min, extend at 3-5 min)",
            "5.4 - HTTP headers extraction",
            "5.5 - CommonHeaders model (DRY principle)",
        ],
    }


# =============================================================================
# Обработчик ошибок
# =============================================================================


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    """Кастомный обработчик HTTP исключений."""
    if exc.status_code == 401:
        return JSONResponse(
            status_code=401,
            content={"message": "Unauthorized"},
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail if isinstance(exc.detail, str) else "Error"},
    )


# =============================================================================
# Запуск приложения
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
