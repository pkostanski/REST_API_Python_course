from typing import List, Dict
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, DuplicateKeyError
from fastapi import HTTPException
import models


class Database:
    def __init__(self):
        client = MongoClient(serverSelectionTimeoutMS=5000)
        try:
            client.server_info()
        except ServerSelectionTimeoutError as e:
            raise HTTPException(status_code=503, detail="Problem with connecting to Database")
        self.users_collection = client['data']['users']

    def get_all_users(self) -> List[models.UserSafe]:
        """
        Method for fetching data from mongoDB about all users.

        :returns:
            List[models.UserSafe]: Returns list of users in UserSafe model format.
        """
        results = self.users_collection.find({})
        return list(results)

    def get_one_user(self, user_email: str) -> models.UserSafe:
        user_data = self.users_collection.find_one({"email": user_email})
        if user_data is None:
            raise HTTPException(status_code=404, detail=f"User with email {user_email} not found in database.")
        return user_data

    def update_user(self, model: models.User) -> Dict[str, str]:
        user_data = self.users_collection.replace_one({"email": model.email}, model.dict())
        if user_data.modified_count == 0:
            raise HTTPException(status_code=404, detail=f"User with email {model.email} not found in database.")
        return {"info": f"User with email {model.email} modified in database."}

    def delete_user(self, user_email: str) -> Dict[str, str]:
        user_data = self.users_collection.delete_one({"email": user_email})
        if user_data.deleted_count == 0:
            raise HTTPException(status_code=404, detail=f"User with email {user_email} not found in database.")
        return {"info": f"User with email {user_email} deleted from database."}

    def add_user(self, model: models.User) -> Dict[str, str]:
        try:
            self.users_collection.insert_one(model.dict())
        except DuplicateKeyError:
            raise HTTPException(status_code=409, detail=f"User with email {model.email} not created (duplicate).")
        return {"info": f"User with email {model.email} added to database."}
