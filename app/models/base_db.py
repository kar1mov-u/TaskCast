from sqlmodel import Field, Relationship, SQLModel
from .project import ProjectInput
from enum import Enum
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
 #   user: "UserDB" = Relationship(back_populates="projects_link")
    # project: "ProjectDB" = Relationship(back_populates="participants")


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


class UserDB(UserInput, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # This is the relationship back to the projects linked to a user
    projects: list["ProjectDB"] = Relationship(
        back_populates="participants",
        link_model=ProjectUserLink
    )
    
    # This relationship is for the intermediate link, which is optional unless you need direct access
   #projects_link: list[ProjectUserLink] = Relationship(back_populates="user")

class AddUser(SQLModel):
    user_id:int
    user_type:UserType
