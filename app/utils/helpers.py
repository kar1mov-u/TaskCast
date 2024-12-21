from passlib.context import CryptContext
from fastapi import HTTPException
from ..database import SessionDep
from sqlmodel import select
from ..models.base_db import ProjectDB,UserDB,ProjectUserLink
pwd_context=CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_pass(plain):
    return pwd_context.hash(plain)

def verify_pass(hash,plain):
    return pwd_context.verify(plain,hash)

def get_project_by_id(id:int, session:SessionDep)->ProjectDB:
    project = session.exec(select(ProjectDB).where(ProjectDB.id==id)).first()
    if not project:
        raise HTTPException(status_code=404, detail="No project found")
    return project

def get_user_by_id(id:int,session:SessionDep) ->UserDB:
    user = session.exec(select(UserDB).where(UserDB.id==id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def check_user_permission(user_id:int, project_id:int, session:SessionDep, allowed_type):
    link_model_entry = session.exec(select(ProjectUserLink).where(ProjectUserLink.project_id==project_id,ProjectUserLink.user_id==user_id)).first()
    if not link_model_entry or link_model_entry.user_type not in allowed_type:
        raise HTTPException(status_code=401, detail="Permission denied")
    return True