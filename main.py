from fastapi import FastAPI, status
from typing import List
import models
from src.database import Database


app = FastAPI()


@app.get("/users", response_model=List[models.UserSafe], tags=["Users"])
def get_all_users():
    """Get all users from db"""
    return Database().get_all_users()


@app.get("/users/{user_email}", response_model=models.UserSafe, tags=["Users"])
def users_one(user_email: str):
    """Get user from database by email."""
    return Database().get_one_user(user_email)


@app.put("/users", tags=["Users"])
def user_update(user: models.User):
    """Update user in database."""
    return Database().update_user(user)


@app.delete("/users/{user_email}", tags=["Users"])
def delete_user_by_email(user_email: str):
    """Delete user from database by email."""
    return Database().delete_user(user_email)


@app.post("/users", status_code=status.HTTP_201_CREATED, tags=["Users"], responses={409: {"model": models.Message}})
def add_user(user: models.User):
    """Add new user to database."""
    return Database().add_user(user)
