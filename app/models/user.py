from sqlmodel import SQLModel,Field,Relationship
from pydantic import EmailStr
from datetime import datetime

class UserInput(SQLModel):
    username:str = Field(nullable=False, unique=True, index=True)
    email:EmailStr = Field(nullable=False, unique=True, index=True)
    full_name : str = Field(nullable=False)
    password: str = Field(nullable=False)


class LoginInput(SQLModel):
    username:str
    password:str

class DeleteUser(SQLModel):
    user_id:int