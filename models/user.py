from pydantic import BaseModel

class User(BaseModel):
    FirstName: str
    LastName: str
    email: str
    password: str # on production ofc hashed


class UserSafe(BaseModel):
    FirstName: str
    LastName: str
    email: str