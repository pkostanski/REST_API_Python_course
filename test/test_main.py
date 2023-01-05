from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from main import app
import models

client = TestClient(app)

test_user1 = models.User(
    FirstName="Krzychu",
    LastName="Drugi",
    email="example.@.com",
    password="somepass"
)

test_user2 = models.User(
    FirstName="Andrzej",
    LastName="Drugi",
    email="example22.@.com",
    password="somepass22"
)


def test_read_docs():
    response = client.get("/docs")
    assert response.status_code == 200
    assert "<title>FastAPI - Swagger UI</title>" in response.text


@patch("main.Database")
def test_users_all(mocked_database: Mock):
    mocked_database.return_value.get_all_users.return_value = [test_user1, test_user2]
    response = client.get("/users")
    expected_result = [
        {
            "FirstName": "Krzychu",
            "LastName": "Drugi",
            "email": "example.@.com",
        },
        {
            "FirstName": "Andrzej",
            "LastName": "Drugi",
            "email": "example22.@.com",
        }
    ]
    assert response.status_code == 200
    assert response.json() == expected_result


@patch("main.Database")
def test_users_all2(mocked_database: Mock):
    database_instance = Mock()
    database_instance.get_all_users.return_value = [test_user1, test_user2]
    mocked_database.return_value = database_instance
    response = client.get("/users")
    expected_result = [
        {
            "FirstName": "Krzychu",
            "LastName": "Drugi",
            "email": "example.@.com",
        },
        {
            "FirstName": "Andrzej",
            "LastName": "Drugi",
            "email": "example22.@.com",
        }
    ]
    assert response.status_code == 200
    assert response.json() == expected_result
