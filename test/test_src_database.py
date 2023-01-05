import pytest
from unittest.mock import patch, Mock, MagicMock
from pymongo.errors import ServerSelectionTimeoutError, DuplicateKeyError
from fastapi import HTTPException
from src.database import Database
import models


mocked_db_data = [
    {
        "id": 1,
        "name": "SomeUser"
    },
    {
        "id": 2,
        "name": "SomeUser2"
    },
    {
        "id": 3,
        "name": "SomeUser3"
    }
]

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

mocked_db_data2 = [test_user1, test_user2]


@patch("src.database.MongoClient")
def test_Database_init(mocked_database):
    database_instance = MagicMock() # mock for magic methods
    database_instance.server_info.return_value = "Some server info"
    database_instance.__getitem__.return_value.__getitem__.return_value = mocked_db_data
    mocked_database.return_value = database_instance
    database_object = Database()
    assert database_object.users_collection == mocked_db_data


@patch("src.database.MongoClient")
def test_database_init_error(mocked_database):
    database_instance = Mock()  # mock for magic methods
    database_instance.server_info.side_effect = ServerSelectionTimeoutError(message="Mocked error.")
    mocked_database.return_value = database_instance
    with pytest.raises(HTTPException) as e_info:
        Database()
    assert "status_code=503, detail='Problem with connecting to Database'" in str(e_info)


@patch("src.database.MongoClient")
def test_Database_init_error2(mocked_database):
    database_instance = Mock()  # mock for magic methods
    database_instance.server_info.side_effect = TypeError()
    mocked_database.return_value = database_instance
    with pytest.raises(TypeError) as e_info:
        Database()


@pytest.fixture
def mocked_database_fix():
    with patch("src.database.MongoClient") as mocked_database:
        database_instance = MagicMock()  # mock for magic methods
        database_instance.server_info.return_value = "Some server info"
        database_instance.__getitem__.return_value.__getitem__.return_value = mocked_db_data2
        mocked_database.return_value = database_instance
        yield mocked_database


def test_database_init2(mocked_database_fix):
    database_object = Database()
    assert database_object.users_collection == mocked_db_data2


def test_database_get_all_users(mocked_database_fix):
    database_object = Database()
    mocked_collection = Mock()
    mocked_collection.find.return_value = test_user1
    database_object.users_collection = mocked_collection
    result = database_object.get_all_users()
    # print(result)
    assert result == [('FirstName', 'Krzychu'), ('LastName', 'Drugi'), ('email', 'example.@.com'), ('password', 'somepass')]


def test_database_get_one_user(mocked_database_fix):
    database_object = Database()
    mocked_collection = Mock()
    mocked_collection.find_one.return_value = test_user1
    database_object.users_collection = mocked_collection
    result = database_object.get_one_user(user_email="MockedEmail")
    assert result == test_user1


def test_database_get_one_user_error(mocked_database_fix):
    database_object = Database()
    mocked_collection = Mock()
    mocked_collection.find_one.return_value = None
    database_object.users_collection = mocked_collection
    with pytest.raises(HTTPException) as e_info:
        database_object.get_one_user(user_email="MockedEmail")
    assert "status_code=404, detail='User with email MockedEmail not found in database.'"


def test_database_update_user(mocked_database_fix):
    database_object = Database()
    mocked_user_data = Mock()
    mocked_user_data.modified_count = 1
    mocked_collection = Mock()
    mocked_collection.replace_one.return_value = mocked_user_data
    database_object.users_collection = mocked_collection
    result = database_object.update_user(model=test_user1)
    assert result == {"info": f"User with email {test_user1.email} modified in database."}


def test_database_update_user_error(mocked_database_fix):
    database_object = Database()
    mocked_user_data = Mock()
    mocked_user_data.modified_count = 0
    mocked_collection = Mock()
    mocked_collection.replace_one.return_value = mocked_user_data
    database_object.users_collection = mocked_collection
    with pytest.raises(HTTPException) as e_info:
        result = database_object.update_user(model=test_user1)
    assert f"status_code=404, detail='User with email {test_user1.email} not found in database.'"


def test_database_delete_user(mocked_database_fix):
    database_object = Database()
    mocked_user_data = Mock()
    mocked_user_data.deleted_count = 1
    mocked_collection = Mock()
    mocked_collection.delete_one.return_value = mocked_user_data
    database_object.users_collection = mocked_collection
    result = database_object.delete_user(user_email="MockedEmail")
    assert result == {"info": "User with email MockedEmail deleted from database."}


def test_database_delete_user_error(mocked_database_fix):
    database_object = Database()
    mocked_user_data = Mock()
    mocked_user_data.deleted_count = 0
    mocked_collection = Mock()
    mocked_collection.delete_one.return_value = mocked_user_data
    database_object.users_collection = mocked_collection
    with pytest.raises(HTTPException) as e_info:
        result = database_object.delete_user(user_email="MockedEmail")
    assert "status_code=404, detail='User with email MockedEmail not found in database.'" in str(e_info)


@pytest.fixture()
def mocked_collection_fix():
    mocked_user_data = Mock()
    mocked_user_data.deleted_count = 1
    mocked_user_data.modified_count = 1
    mocked_collection = Mock()
    mocked_collection.delete_one.return_value = mocked_user_data
    mocked_collection.replace_one.return_value = mocked_user_data
    return mocked_collection


@pytest.fixture()
def mocked_collection_fix_error():
    mocked_user_data = Mock()
    mocked_user_data.deleted_count = 1
    mocked_user_data.modified_count = 1
    mocked_collection = Mock()
    mocked_collection.insert_one.side_effect = DuplicateKeyError(error="MockedError")
    return mocked_collection


def test_database_delete_user2(mocked_database_fix, mocked_collection_fix):
    database_object = Database()
    database_object.users_collection = mocked_collection_fix
    result = database_object.delete_user(user_email="MockedEmail")
    assert result == {"info": "User with email MockedEmail deleted from database."}


def test_database_add_user(mocked_database_fix, mocked_collection_fix):
    database_object = Database()
    database_object.users_collection = mocked_collection_fix
    result = database_object.add_user(model=test_user1)
    assert result == {"info": f"User with email {test_user1.email} added to database."}


def test_database_add_user_error(mocked_database_fix, mocked_collection_fix_error):
    database_object = Database()
    database_object.users_collection = mocked_collection_fix_error
    with pytest.raises(HTTPException) as e_info:
        database_object.add_user(model=test_user1)
    assert f"status_code=409, detail='User with email {test_user1.email} not created (duplicate).'" in str(e_info)
