from fastapi import APIRouter,Depends
from ..utils.auth import get_current_user
from ..models.base_db import ProjectUserLink
from sqlmodel import select
from ..models.base_db import UserDB,UserReturn
from ..database import SessionDep
router = APIRouter(tags=['user'])

@router.get('/users/me',response_model=UserReturn)
def get_my_user(session:SessionDep,user:UserDB=Depends(get_current_user)):
    
    return_obj = UserReturn(username=user.username,email= user.email, full_name = user.full_name)
    return return_obj
