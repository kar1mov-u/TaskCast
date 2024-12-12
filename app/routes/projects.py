from fastapi import APIRouter, HTTPException,Depends
from ..models.project import ProjectInput,ProjectParticipant,ProjectRead
from ..models.base_db import ProjectDB
from sqlalchemy.orm import joinedload
from ..database import SessionDep
from sqlmodel import select
from ..utils.auth import get_current_user
router = APIRouter(tags=['projects'])

@router.post('/projects/create')
def create_project(project_data:ProjectInput, session:SessionDep,user=Depends(get_current_user)):
    existing_project = session.exec(
        select(ProjectDB).where(ProjectDB.name == project_data.name)
    ).first()
    if existing_project:
        raise HTTPException(status_code=400, detail="A project with this name already exists")
    
    project_db = ProjectDB(**project_data.model_dump(),creator_id=user.id)
    session.add(project_db)
    project_db.participants.append(user)
    session.commit()
    session.refresh(project_db)
    return project_db
    
    
@router.get('/projects/{id}',response_model=ProjectRead)
def get_project(id:int, session:SessionDep):
    project_db= session.exec(select(ProjectDB).where(ProjectDB.id==id)).first()
    project = ProjectRead(**project_db.model_dump(),
                          participants=[ProjectParticipant(user_id=part.id, username=part.username) for part in project_db.participants])
    return project