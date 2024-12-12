from sqlmodel import Field,Relationship,SQLModel
from .project import ProjectInput
from .user import UserInput
from datetime import datetime


class ProjectUserLink(SQLModel, table=True):
    project_id :int=Field(foreign_key="projectdb.id", primary_key=True)
    user_id:int=Field(foreign_key="userdb.id", primary_key=True)



class ProjectDB(ProjectInput,table=True):
    id: int|None=Field(default=None,primary_key=True)
    creator_id:int=Field(foreign_key="userdb.id")
    updated_at :datetime=Field(default_factory=datetime.utcnow)
    created_at :datetime=Field(default_factory=datetime.utcnow)
    
    
    participants :list["UserDB"] = Relationship(
        back_populates="projects",
        link_model=ProjectUserLink
    )
    
class UserDB(UserInput, table=True):
    id: int| None=Field(default=None,primary_key=True)
    created_at: datetime =Field(default_factory=datetime.utcnow)
    projects :list["ProjectDB"]=Relationship(
        back_populates="participants",
        link_model=ProjectUserLink
    )
    
     