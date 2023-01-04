from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel
from pymongo import MongoClient


app = FastAPI()


class User(BaseModel):
    FirstName: str
    LastName: str
    email: str
    password: str # on production ofc hashed


@app.get("/", tags=["category1"])
def read_root():
    """This endpoint is for test only"""
    return {"Hello": "from root"}

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item name": item.name, "item id": item.id}
