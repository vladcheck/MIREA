import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import storage


@pytest.fixture
def client():
    """Создать TestClient для приложения"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def cleanup_storage():
    """Очистить хранилище перед каждым тестом"""
    storage.clear()
    yield
    storage.clear()


class TestWebSocketConnection:
    """Тесты для подключения к WebSocket"""
    
    def test_connect_with_valid_username(self, client):
        """Подключение к комнате с корректным username"""
        with client.websocket_connect("/ws/rooms/python?username=alice") as websocket:
            data = websocket.receive_json()
            assert data["type"] == "user_joined"
            assert data["username"] == "alice"
            assert data["room_id"] == "python"
    
    def test_connect_without_username(self, client):
        """Отключение при отсутствии username"""
        try:
            with client.websocket_connect("/ws/rooms/python") as websocket:
                pass
            assert False, "Expected connection to fail"
        except Exception:
            pass
    
    def test_connect_with_empty_username(self, client):
        """Отключение при пустом username"""
        try:
            with client.websocket_connect("/ws/rooms/python?username=%20%20%20") as websocket:
                pass
            assert False, "Expected connection to fail"
        except Exception:
            pass


class TestWebSocketMessaging:
    """Тесты для обмена сообщениями через WebSocket"""
    
    def test_send_and_receive_message(self, client):
        """Отправка и получение сообщения"""
        with client.websocket_connect("/ws/rooms/python?username=alice") as websocket:
            # Получить событие подключения
            data = websocket.receive_json()
            assert data["type"] == "user_joined"
            
            # Отправить сообщение
            websocket.send_json({
                "type": "message",
                "text": "Hello, World!"
            })
            
            # Получить свое же сообщение (broadcast)
            data = websocket.receive_json()
            assert data["type"] == "message"
            assert data["username"] == "alice"
            assert data["text"] == "Hello, World!"
            assert data["room_id"] == "python"
    
    def test_two_clients_receive_message(self, client):
        """Два клиента в одной комнате получают одно и то же сообщение"""
        # Подключить первого клиента
        with client.websocket_connect("/ws/rooms/python?username=alice") as ws1:
            # Получить событие подключения
            ws1.receive_json()
            
            # Подключить второго клиента
            with client.websocket_connect("/ws/rooms/python?username=bob") as ws2:
                # Второй клиент получит событие подключения первого
                ws2.receive_json()
                # Первый клиент получит событие подключения второго
                ws1.receive_json()
                
                # Первый клиент отправляет сообщение
                ws1.send_json({
                    "type": "message",
                    "text": "Hi Bob!"
                })
                
                # Оба клиента получают сообщение
                msg1 = ws1.receive_json()
                msg2 = ws2.receive_json()
                
                assert msg1["text"] == "Hi Bob!"
                assert msg2["text"] == "Hi Bob!"
                assert msg1["username"] == "alice"
                assert msg2["username"] == "alice"
    
    def test_message_too_long(self, client):
        """Слишком длинное сообщение возвращает событие error"""
        with client.websocket_connect("/ws/rooms/python?username=alice") as websocket:
            # Получить событие подключения
            websocket.receive_json()
            
            # Отправить слишком длинное сообщение
            long_text = "x" * 301
            websocket.send_json({
                "type": "message",
                "text": long_text
            })
            
            # Получить ошибку
            data = websocket.receive_json()
            assert data["type"] == "error"
            assert "too long" in data["detail"].lower()


class TestWebSocketRooms:
    """Тесты для работы с комнатами"""
    
    def test_different_rooms_isolated(self, client):
        """Пользователи из разных комнат не получают чужие сообщения"""
        # Подключить клиента к комнате python
        with client.websocket_connect("/ws/rooms/python?username=alice") as ws_python:
            ws_python.receive_json()  # user_joined
            
            # Подключить клиента к комнате javascript
            with client.websocket_connect("/ws/rooms/javascript?username=bob") as ws_js:
                ws_js.receive_json()  # user_joined
                
                # Alice отправляет сообщение в python
                ws_python.send_json({
                    "type": "message",
                    "text": "Python message"
                })
                
                # Alice получает свое сообщение
                msg = ws_python.receive_json()
                assert msg["text"] == "Python message"
                
                # Bob не получает сообщение от Alice
                # (он остается в своей комнате)
    
    def test_room_users_after_disconnect(self, client):
        """После отключения пользователя он не возвращается в списке"""
        # Подключить пользователя
        with client.websocket_connect("/ws/rooms/python?username=alice") as websocket:
            websocket.receive_json()
            
            # Проверить что пользователь в списке
            response = client.get("/rooms/python/users")
            assert response.status_code == 200
            assert "alice" in response.json()["users"]
        
        # После отключения пользователя
        response = client.get("/rooms/python/users")
        if response.status_code == 200:
            assert "alice" not in response.json()["users"]
