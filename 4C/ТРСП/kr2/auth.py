import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
from dataclasses import dataclass, field
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired


@dataclass
class SessionData:
    """
    Данные сессии пользователя (Задание 5.3).
    """

    user_id: str  # UUID пользователя
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(
        default_factory=lambda: datetime.now() + timedelta(minutes=5)
    )

    def is_valid(self) -> bool:
        """Проверка валидности сессии (5 минут без активности)."""
        return datetime.now() < self.expires_at

    def should_extend(self) -> bool:
        """
        Проверка необходимости продления сессии (Задание 5.3).
        Возвращает True, если прошло от 3 до 5 минут с последней активности.
        """
        now = datetime.now()
        time_since_activity = (now - self.last_activity).total_seconds()

        # Продлеваем если прошло от 180 до 300 секунд (3-5 минут)
        return 180 <= time_since_activity < 300

    def extend(self):
        """Продление сессии на 5 минут с момента текущей активности."""
        self.last_activity = datetime.now()
        self.expires_at = self.last_activity + timedelta(minutes=5)


class SessionManager:
    """
    Менеджер сессий с криптографической подписью (Задания 5.2, 5.3).
    В production следует использовать Redis или базу данных.
    """

    # Секретный ключ для подписи cookie (в production хранить в env variables)
    SECRET_KEY = "super-secret-key-change-in-production-2026"
    SESSION_COOKIE_NAME = "session_token"
    SESSION_DURATION_MINUTES = 5
    EXTEND_THRESHOLD_MINUTES = 3

    def __init__(self):
        # Хранилище сессий: user_id -> SessionData
        self._sessions: Dict[str, SessionData] = {}

        # Инициализация подписывателя
        self._serializer = URLSafeTimedSerializer(self.SECRET_KEY)

        # Тестовые пользователи (в production использовать БД)
        self._users: Dict[str, dict] = {
            "user123": {
                "password": self._hash_password("password123"),
                "email": "user123@example.com",
                "full_name": "User One Two Three",
                "user_id": str(uuid.uuid4()),
            },
            "admin": {
                "password": self._hash_password("admin123"),
                "email": "admin@example.com",
                "full_name": "Administrator",
                "user_id": str(uuid.uuid4()),
            },
            "alice": {
                "password": self._hash_password("alice123"),
                "email": "alice@example.com",
                "full_name": "Alice Smith",
                "user_id": str(uuid.uuid4()),
            },
        }

    @staticmethod
    def _hash_password(password: str) -> str:
        """Хеширование пароля (упрощённое для демонстрации)."""
        return hashlib.sha256(password.encode()).hexdigest()

    def generate_token(self, user_id: str, timestamp: int) -> str:
        """
        Генерация подписанного токена сессии (Задание 5.2, 5.3).
        Формат: <user_id>.<timestamp>.<signature>
        """
        # Создаём payload с user_id и timestamp
        payload = {"user_id": user_id, "timestamp": timestamp}

        # Подписываем payload
        token = self._serializer.dumps(payload)

        return token

    def verify_token(self, token: str, max_age: int = 300) -> Optional[Dict]:
        """
        Проверка и верификация токена сессии.
        Возвращает payload при успехе, None при неудаче.
        """
        try:
            # Проверяем подпись и извлекаем payload
            payload = self._serializer.loads(token, max_age=max_age)
            return payload
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        except Exception:
            return None

    def authenticate(self, username: str, password: str) -> Optional[Tuple[str, str]]:
        """
        Аутентификация пользователя (Задания 5.1, 5.2, 5.3).
        Возвращает кортеж (user_id, token) при успехе, None при неудаче.
        """
        user = self._users.get(username)
        if not user:
            return None

        password_hash = self._hash_password(password)
        if user["password"] != password_hash:
            return None

        user_id = user["user_id"]
        now = datetime.now()
        timestamp = int(now.timestamp())

        # Создаём сессию
        session = SessionData(
            user_id=user_id,
            username=username,
            email=user.get("email"),
            full_name=user.get("full_name"),
            created_at=now,
            last_activity=now,
            expires_at=now + timedelta(minutes=self.SESSION_DURATION_MINUTES),
        )
        self._sessions[user_id] = session

        # Генерируем подписанный токен
        token = self.generate_token(user_id, timestamp)

        return (user_id, token)

    def get_session(self, token: str) -> Optional[SessionData]:
        """
        Получение данных сессии по токену с проверкой подписи (Задание 5.3).
        """
        # Верифицируем токен
        payload = self.verify_token(token, max_age=300)  # 5 минут
        if not payload:
            return None

        user_id = payload.get("user_id")
        if not user_id:
            return None

        session = self._sessions.get(user_id)
        if not session or not session.is_valid():
            # Удаляем невалидную сессию
            if session:
                del self._sessions[user_id]
            return None

        return session

    def extend_session(self, user_id: str) -> bool:
        """
        Продление сессии при активности (Задание 5.3).
        Возвращает True если сессия была продлена.
        """
        session = self._sessions.get(user_id)
        if not session:
            return False

        if session.should_extend():
            session.extend()
            return True

        return False

    def invalidate_session(self, user_id: str) -> bool:
        """Удаление сессии (logout)."""
        if user_id in self._sessions:
            del self._sessions[user_id]
            return True
        return False

    def cleanup_expired(self) -> int:
        """Очистка истёкших сессий. Возвращает количество удалённых."""
        expired = [
            user_id
            for user_id, session in self._sessions.items()
            if not session.is_valid()
        ]
        for user_id in expired:
            del self._sessions[user_id]
        return len(expired)

    def get_user_by_username(self, username: str) -> Optional[dict]:
        """Получение пользователя по имени."""
        return self._users.get(username)


# Глобальный экземпляр менеджера сессий
session_manager = SessionManager()
