from fastapi import FastAPI, HTTPException
from typing import Optional, List
from pydantic import BaseModel
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError


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


@app.get("/users", response_model=List[UserSafe], tags=["users"])
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

