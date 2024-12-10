from sqlmodel import SQLModel,Field
from pydantic import EmailStr
from datetime import datetime


class UserInput(SQLModel):
    username:str = Field(nullable=False, unique=True, index=True)
    email:EmailStr = Field(nullable=False, unique=True, index=True)
    full_name : str = Field(nullable=False)
    password: str = Field(nullable=False)

class UserDB(UserInput, table=True):
    id: int| None=Field(default=None,primary_key=True)
    created_at: datetime =Field(default_factory=datetime.utcnow)
    
class LoginInput(SQLModel):
    username:str
    password:str
