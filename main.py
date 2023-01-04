from fastapi import FastAPI, HTTPException, status
from typing import Optional, List
from pydantic import BaseModel
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, DuplicateKeyError


app = FastAPI()


class User(BaseModel):
    FirstName: str
    LastName: str
    email: str
    password: str # on production ofc hashed


class UserSafe(BaseModel):
    FirstName: str
    LastName: str
    email: str


@app.get("/users", response_model=List[UserSafe], tags=["Users"])
def get_all_users():
    """Get all users from db"""
    client = MongoClient(serverSelectionTimeoutMS=5000)
    users_collection = client['data']['users']
    try:
        client.server_info()
    except ServerSelectionTimeoutError as e:
        raise HTTPException(status_code=503, detail="Problem with connecting to Database")
    res = users_collection.find({})
    res2 = list(res)
    print(list(res))
    return res2


@app.get("/users/{user_email}", response_model=UserSafe, tags=["Users"])
def users_one(user_email: str):
    """Get user from database by email."""
    client = MongoClient(serverSelectionTimeoutMS=5000)
    users_collection = client['data']['users']
    try:
        client.server_info()
    except ServerSelectionTimeoutError as e:
        raise HTTPException(status_code=503, detail="Problem with connecting to database.")
    user_data = users_collection.find_one({"email": user_email})
    if user_data is None:
        raise HTTPException(status_code=404, detail=f"User with email {user_email} not found in database.")
    return user_data


@app.put("/users", tags=["Users"])
def user_update(user: User):
    """Update user in database."""
    client = MongoClient(serverSelectionTimeoutMS=5000)
    users_collection = client['data']['users']
    try:
        client.server_info()
    except ServerSelectionTimeoutError as e:
        raise HTTPException(status_code=503, detail="Problem with connecting to Database")
    user_data = users_collection.replace_one({"email": user.email}, user.dict())
    if user_data.modified_count == 0:
        raise HTTPException(status_code=404, detail=f"User with email {user.email} not found in database.")
    return {"info": f"User with email {user.email} modified in database."}


@app.delete("/users/{user_email}", tags=["Users"])
def delete_user_by_email(user_email: str):
    """Delete user from database by email."""
    client = MongoClient(serverSelectionTimeoutMS=5000)
    users_collection = client['data']['users']
    try:
        client.server_info()
    except ServerSelectionTimeoutError as e:
        raise HTTPException(status_code=503, detail="Problem with connecting to Database")
    user_data = users_collection.delete_one({"email": user_email})
    if user_data.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"User with email {user_email} not found in database.")
    return {"info": f"User with email {user_email} deleted from database."}


class Message(BaseModel):
    detail: str


@app.post("/users", status_code=status.HTTP_201_CREATED, tags=["Users"], responses={409: {"model": Message}})
def add_user(user: User):
    """Add new user to database."""
    client = MongoClient(serverSelectionTimeoutMS=5000)
    users_collection = client['data']['users']
    try:
        client.server_info()
    except ServerSelectionTimeoutError as e:
        raise HTTPException(status_code=503, detail="Problem with connecting to Database")
    try:
        users_collection.insert_one(user.dict())
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail=f"User with email {user.email} not created (duplicate).")
    return {"info": f"User with email {user.email} added to database."}
