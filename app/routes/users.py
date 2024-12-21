from fastapi import APIRouter,Depends
from ..utils.auth import get_current_user
from ..models.base_db import ProjectUserLink,ProjectDB
from sqlmodel import select
from ..models.base_db import UserDB,UserReturn
from ..database import SessionDep
router = APIRouter(tags=['user'])

@router.get('/users/me',response_model=UserReturn)
def get_my_user(session:SessionDep,user:UserDB=Depends(get_current_user)):
    
    #Get the ID of the project where user participated
    projects_link = session.exec(select(ProjectUserLink).where(ProjectUserLink.user_id ==user.id)).all()
    #Extract only Project ID's
    project_ids = set([p.project_id for p in projects_link])
    #Get all the Projects from db
    projects_db = session.exec(select(ProjectDB).where(ProjectDB.id.in_(project_ids))).all()
    #Create response object with ID-name,tag mapping for every project
    projects_return = [{"id":project.id, "name":project.name, "tag":project.tag}for project in projects_db]

    return_obj = UserReturn(username=user.username,email= user.email, full_name = user.full_name,id=user.id,projects=projects_return)
    
        
    
    return return_obj
