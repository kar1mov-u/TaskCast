from fastapi import APIRouter,HTTPException
from ..models.user import UserInput,LoginInput
from ..models.base_db import UserDB
from ..database import SessionDep
from sqlmodel import select
from sqlalchemy.sql import or_
from sqlalchemy.exc import IntegrityError
from ..utils.helpers import hash_pass,verify_pass
from ..utils.auth import create_access_token
from datetime import timedelta
router = APIRouter(tags=["auth"])

@router.post('/register')
def register(user_data:UserInput, session:SessionDep):
    try:
        user_db = UserDB(**user_data.model_dump())
        user_db.password = hash_pass(user_db.password)
        session.add(user_db)
        session.commit()
        session.refresh(user_db)
        return user_db
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=400, detail="Email or Username is already in use")
    
    
@router.post('/login')
def login(user_data:LoginInput, session:SessionDep):
    user_db = session.exec(select(UserDB).where(or_(UserDB.email==user_data.username,UserDB.username==user_data.username))).first()
    if not user_db:
        raise HTTPException(status_code=404, detail="There is no such user")
    if not verify_pass(user_db.password,user_data.password):
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    access_token_expires = timedelta(minutes=90)
    
    token = create_access_token(data={"sub":user_db.username},expires_delta=access_token_expires)
    return token
    