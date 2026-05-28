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


class TestTaskCreation:
    """Тесты для создания задач"""
    
    def test_create_task_success(self, client):
        """Успешное создание задачи"""
        response = client.post(
            "/tasks",
            json={
                "title": "Подготовить тесты",
                "description": "Написать интеграционные тесты",
                "status": "todo",
                "priority": 4
            },
            headers={"X-User-Id": "10"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Подготовить тесты"
        assert data["owner_id"] == 10
        assert data["id"] == 1
    
    def test_create_task_short_title(self, client):
        """Ошибка 422 если title короче 3 символов"""
        response = client.post(
            "/tasks",
            json={
                "title": "AB",
                "status": "todo",
                "priority": 2
            },
            headers={"X-User-Id": "10"}
        )
        assert response.status_code == 422
    
    def test_create_task_without_user_id(self, client):
        """Ошибка 401 если нет заголовка X-User-Id"""
        response = client.post(
            "/tasks",
            json={
                "title": "Новая задача",
                "status": "todo",
                "priority": 2
            }
        )
        assert response.status_code == 401


class TestTaskRetrieval:
    """Тесты для получения задач"""
    
    def test_get_user_tasks(self, client):
        """Пользователь видит только свои задачи"""
        # Создать задачи для пользователя 1
        client.post(
            "/tasks",
            json={"title": "Задача 1", "status": "todo", "priority": 1},
            headers={"X-User-Id": "1"}
        )
        client.post(
            "/tasks",
            json={"title": "Задача 2", "status": "done", "priority": 2},
            headers={"X-User-Id": "1"}
        )
        
        # Создать задачи для пользователя 2
        client.post(
            "/tasks",
            json={"title": "Задача 3", "status": "todo", "priority": 1},
            headers={"X-User-Id": "2"}
        )
        
        # Проверить что пользователь 1 видит только свои задачи
        response = client.get("/tasks", headers={"X-User-Id": "1"})
        assert response.status_code == 200
        assert len(response.json()) == 2
    
    def test_filter_tasks_by_status(self, client):
        """Фильтрация задач по статусу"""
        client.post(
            "/tasks",
            json={"title": "Задача 1", "status": "todo", "priority": 1},
            headers={"X-User-Id": "1"}
        )
        client.post(
            "/tasks",
            json={"title": "Задача 2", "status": "done", "priority": 2},
            headers={"X-User-Id": "1"}
        )
        
        response = client.get("/tasks?status=done", headers={"X-User-Id": "1"})
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["status"] == "done"
    
    def test_filter_tasks_by_priority(self, client):
        """Фильтрация задач по минимальному приоритету"""
        client.post(
            "/tasks",
            json={"title": "Задача 1", "status": "todo", "priority": 1},
            headers={"X-User-Id": "1"}
        )
        client.post(
            "/tasks",
            json={"title": "Задача 2", "status": "todo", "priority": 4},
            headers={"X-User-Id": "1"}
        )
        
        response = client.get("/tasks?min_priority=3", headers={"X-User-Id": "1"})
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["priority"] == 4


class TestTaskUpdate:
    """Тесты для обновления задач"""
    
    def test_update_task_status_success(self, client):
        """Успешное изменение статуса задачи"""
        # Создать задачу
        create_response = client.post(
            "/tasks",
            json={"title": "Задача", "status": "todo", "priority": 2},
            headers={"X-User-Id": "1"}
        )
        task_id = create_response.json()["id"]
        
        # Обновить статус
        response = client.patch(
            f"/tasks/{task_id}/status",
            json={"status": "done"},
            headers={"X-User-Id": "1"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "done"


class TestTaskDeletion:
    """Тесты для удаления задач"""
    
    def test_delete_task_success(self, client):
        """Успешное удаление задачи"""
        # Создать задачу
        create_response = client.post(
            "/tasks",
            json={"title": "Задача", "status": "todo", "priority": 2},
            headers={"X-User-Id": "1"}
        )
        task_id = create_response.json()["id"]
        
        # Удалить задачу
        response = client.delete(f"/tasks/{task_id}", headers={"X-User-Id": "1"})
        assert response.status_code == 204
        
        # Проверить что задача удалена
        get_response = client.get(f"/tasks/{task_id}", headers={"X-User-Id": "1"})
        assert get_response.status_code == 404


class TestTaskErrors:
    """Тесты для обработки ошибок"""
    
    def test_get_nonexistent_task(self, client):
        """Ошибка 404 при обращении к несуществующей задаче"""
        response = client.get("/tasks/999", headers={"X-User-Id": "1"})
        assert response.status_code == 404
    
    def test_get_other_user_task(self, client):
        """Ошибка 404 при обращении к чужой задаче"""
        # Создать задачу для пользователя 1
        create_response = client.post(
            "/tasks",
            json={"title": "Задача", "status": "todo", "priority": 2},
            headers={"X-User-Id": "1"}
        )
        task_id = create_response.json()["id"]
        
        # Попытаться получить задачу от пользователя 2
        response = client.get(f"/tasks/{task_id}", headers={"X-User-Id": "2"})
        assert response.status_code == 404


class TestHealthCheck:
    """Тесты для проверки здоровья приложения"""
    
    def test_health_check_local(self, client):
        """Проверка маршрута /health"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
