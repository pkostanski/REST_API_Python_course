import pytest
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


@pytest.fixture
def mocked_database_fix(mocker):
    return mocker.patch("main.Database")


@pytest.fixture
def mocked_database_fix2():
    with patch("main.Database") as mocked_database:
        database_instance = Mock()
        database_instance.get_all_users.return_value = [test_user1, test_user2]
        database_instance.get_one_user.return_value = test_user1
        database_instance.update_user.return_value = {"info": "User with email SomeMockedEmail@mock.com modified in database."}
        database_instance.delete_user.return_value = {"info": "User with email SomeMockedEmail@mock.com deleted from database."}
        database_instance.add_user.return_value = {"info": "User with email SomeMockedEmail@mock.com added to database."}
        mocked_database.return_value = database_instance
        yield mocked_database


def test_users_all2(mocked_database_fix: Mock):
    database_instance = Mock()
    database_instance.get_all_users.return_value = [test_user1, test_user2]
    mocked_database_fix.return_value = database_instance
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


def test_users_all3(mocked_database_fix2: Mock):
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


def test_users_one(mocked_database_fix2):
    response = client.get("/users/testemail@m.com")
    expected_result = {
            "FirstName": "Krzychu",
            "LastName": "Drugi",
            "email": "example.@.com",
        }
    assert response.status_code == 200
    assert response.json() == expected_result


def test_user_update(mocked_database_fix2):
    response = client.put("/users", json=test_user1.dict())
    assert response.status_code == 200
    assert response.json() == {"info": "User with email SomeMockedEmail@mock.com modified in database."}


def test_delete_user(mocked_database_fix2):
    response = client.delete("/users/testemail@m.com")
    assert response.status_code == 200
    assert response.json() == {"info": "User with email SomeMockedEmail@mock.com deleted from database."}


def test_add_user(mocked_database_fix2):
    response = client.post("/users", json=test_user1.dict())
    assert response.status_code == 201
    assert response.json() == {"info": "User with email SomeMockedEmail@mock.com added to database."}
