from sqlmodel import Field, Relationship, SQLModel
from .project import ProjectInput,ProjectParticipant
from enum import Enum
from typing import Optional
from .user import UserInput
from datetime import datetime

class UserType(str, Enum):
    CREATOR = "creator"
    MODERATOR = "moderator"
    USER = "user"


class ProjectUserLink(SQLModel, table=True):
    project_id: int = Field(foreign_key="projectdb.id", primary_key=True)
    user_id: int = Field(foreign_key="userdb.id", primary_key=True)
    user_type: UserType = Field(nullable=False, default=UserType.USER)

class ProjectDB(ProjectInput, table=True):
    id: int | None = Field(default=None, primary_key=True)
    creator_id: int = Field(foreign_key="userdb.id")
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Ensure you have only one relationship to link participants and projects.
    participants: list["UserDB"] = Relationship(
        back_populates="projects",
        link_model=ProjectUserLink
    )
    tasks:list["TasksDB"] = Relationship(back_populates="project")
    
class ProjectRead(ProjectInput):
    participants:list[ProjectParticipant]
    tasks:list["TaskRead"]
    id:int
    created_at:datetime
    updated_at:datetime


class UserTaskLink(SQLModel,table=True):
    user_id:int = Field(foreign_key="userdb.id",primary_key=True)
    task_id:int =Field(foreign_key="tasksdb.id",primary_key=True)

class UserDB(UserInput, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # This is the relationship back to the projects linked to a user
    projects: list["ProjectDB"] = Relationship(
        back_populates="participants",
        link_model=ProjectUserLink
    )
    tasks: list["TasksDB"] = Relationship(
        link_model=UserTaskLink,
        back_populates="assigned_users"
    )
    
    # This relationship is for the intermediate link, which is optional unless you need direct access
   #projects_link: list[ProjectUserLink] = Relationship(back_populates="user")

class AddUser(SQLModel):
    user_id:int
    user_type:UserType


class UserReturn(SQLModel):
    id:int
    username:str
    email:str
    full_name:str
    projects:list[dict]

class TaskInput(SQLModel):
    title:str
    description:Optional[str] =None
    assigned_users:list[int]
    parent_id:Optional[int]=None
    


class TasksDB(SQLModel, table=True):  # Ensure it's set as a database table
    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    parent_id: Optional[int] = Field(default=None, foreign_key="tasksdb.id")  # Reference the same table
    parent: Optional["TasksDB"] = Relationship(back_populates="children", sa_relationship_kwargs={"remote_side": "TasksDB.id"})
    children: Optional[list["TasksDB"]] = Relationship(back_populates="parent")  # A task can have multiple children
    assigned_users: list["UserDB"] = Relationship(back_populates="tasks",link_model=UserTaskLink)
    creator_id: int
    creator_name:str
    project_id: int = Field(foreign_key="projectdb.id")
    project: "ProjectDB" = Relationship(back_populates="tasks")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserAssigned(SQLModel):
    username:str
    id:int

class TaskRead(SQLModel):
    title: str
    description: Optional[str] = None
    parent_id:Optional[int] =None
    asassigned_users: Optional[list["UserAssigned"]]="Nigas"
    creator_id:int
    creator_name:str
    created_at:datetime