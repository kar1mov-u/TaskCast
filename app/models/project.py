from __future__ import annotations 

from enum import Enum
from sqlmodel import SQLModel,Field,Relationship
from datetime import datetime




class ProjectTag(str,Enum):
    PERSONAL = "personal"
    WORK = "work"
    STUDY = "study"
    


class ProjectInput(SQLModel):
    name: str = Field(nullable=False)
    description: str| None=""
    tag: ProjectTag = Field(nullable=False)

class ProjectParticipant(SQLModel):
    username:str
    user_id:int
    user_type:str
    


    

