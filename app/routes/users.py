from fastapi import APIRouter,Depends
from ..utils.auth import get_current_user
router = APIRouter(tags=['user'])

@router.get('/users/me')
def get_my_user(user=Depends(get_current_user)):
    print(user.projects)
    return user
