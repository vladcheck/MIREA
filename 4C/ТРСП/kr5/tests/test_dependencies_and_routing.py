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


class TestUsers:
    """Тесты для маршрутов пользователей"""
    
    def test_get_current_user(self, client):
        """Маршрут /users/me возвращает текущего пользователя"""
        response = client.get("/users/me", headers={"X-User-Id": "10", "X-User-Role": "admin"})
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 10
        assert data["role"] == "admin"
    
    def test_get_current_user_without_header(self, client):
        """Пользователь без заголовка X-User-Id получает 401"""
        response = client.get("/users/me")
        assert response.status_code == 401


class TestAdminAccess:
    """Тесты для проверки прав администратора"""
    
    def test_admin_get_stats(self, client):
        """Администратор получает статистику по всем задачам"""
        # Создать несколько задач от разных пользователей
        client.post(
            "/tasks",
            json={"title": "Задача 1", "status": "todo", "priority": 1},
            headers={"X-User-Id": "1"}
        )
        client.post(
            "/tasks",
            json={"title": "Задача 2", "status": "done", "priority": 2},
            headers={"X-User-Id": "2"}
        )
        client.post(
            "/tasks",
            json={"title": "Задача 3", "status": "done", "priority": 3},
            headers={"X-User-Id": "3"}
        )
        
        # Получить статистику как администратор
        response = client.get("/admin/stats", headers={"X-User-Id": "1", "X-User-Role": "admin"})
        assert response.status_code == 200
        data = response.json()
        assert data["total_tasks"] == 3
        assert data["by_status"]["todo"] == 1
        assert data["by_status"]["done"] == 2
    
    def test_regular_user_cannot_access_admin(self, client):
        """Обычный пользователь получает 403 при обращении к /admin/stats"""
        response = client.get("/admin/stats", headers={"X-User-Id": "1", "X-User-Role": "user"})
        assert response.status_code == 403
    
    def test_admin_delete_other_user_task(self, client):
        """Администратор может удалить чужую задачу"""
        # Создать задачу от обычного пользователя
        create_response = client.post(
            "/tasks",
            json={"title": "Задача", "status": "todo", "priority": 2},
            headers={"X-User-Id": "1"}
        )
        task_id = create_response.json()["id"]
        
        # Администратор удаляет чужую задачу
        response = client.delete(
            f"/admin/tasks/{task_id}",
            headers={"X-User-Id": "2", "X-User-Role": "admin"}
        )
        assert response.status_code == 204
        
        # Проверить что задача удалена
        get_response = client.get(f"/tasks/{task_id}", headers={"X-User-Id": "1"})
        assert get_response.status_code == 404


class TestTaskAccessControl:
    """Тесты для управления доступом к задачам"""
    
    def test_user_cannot_delete_other_task(self, client):
        """Обычный пользователь не может удалить чужую задачу"""
        # Создать задачу от пользователя 1
        create_response = client.post(
            "/tasks",
            json={"title": "Задача", "status": "todo", "priority": 2},
            headers={"X-User-Id": "1"}
        )
        task_id = create_response.json()["id"]
        
        # Пользователь 2 пытается удалить задачу
        response = client.delete(
            f"/tasks/{task_id}",
            headers={"X-User-Id": "2"}
        )
        assert response.status_code == 404
    
    def test_all_task_routes_require_auth(self, client):
        """Все маршруты /tasks требуют авторизации"""
        routes = [
            ("GET", "/tasks"),
            ("POST", "/tasks"),
        ]
        
        for method, route in routes:
            if method == "GET":
                response = client.get(route)
            else:
                response = client.post(route, json={"title": "Test", "priority": 1})
            
            assert response.status_code == 401, f"{method} {route} should require auth"


class TestSwaggerTags:
    """Тесты для проверки тегов в Swagger UI"""
    
    def test_openapi_schema(self, client):
        """В OpenAPI схеме маршруты сгруппированы по тегам"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        
        # Проверить что есть теги
        assert "tags" in schema
        tag_names = [tag["name"] for tag in schema["tags"]]
        
        assert "tasks" in tag_names
        assert "users" in tag_names
        assert "admin" in tag_names
