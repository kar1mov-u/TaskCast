import jwt
from jwt.exceptions import InvalidTokenError
from ..database import SessionDep
from ..models.base_db import UserDB
from sqlmodel import select
from sqlalchemy.sql import or_
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends,HTTPException
from pydantic import BaseModel
from datetime import datetime
from datetime import timedelta,timezone

from dotenv import load_dotenv
import os

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login')
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGHORITH = os.getenv("ALGHORITH")
ACCESS_TOKEN_EXPIRE_MINUTE= os.getenv("ACCESS_TOKEN_EXPIRE_MINUTE")

class Token(BaseModel):
    token_type:str
    access_token:str
    
def create_access_token(data:dict, expires_delta:timedelta|None=None):
    to_decode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc)+expires_delta
    else:
        expire = datetime.now(timezone.utc)+timedelta(minutes=90)
    to_decode.update({"exp":expire})
    encoded_jwt = jwt.encode(to_decode, SECRET_KEY, algorithm=ALGHORITH)
    return Token(token_type="Bearer", access_token=encoded_jwt)


def get_current_user(session:SessionDep, token:str=Depends(oauth2_scheme))->UserDB:
    credentials_execption = HTTPException(
        status_code=401,
        detail="Couldn't validate credentials",
        headers={"WWW-Authenticate":"Bearer"}
    )
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGHORITH])
        username = payload.get('sub')
        if not username:
            raise credentials_execption
    except InvalidTokenError:
        raise credentials_execption
    
    user_db = session.exec(select(UserDB).where(or_(UserDB.email==username,UserDB.username==username))).first()
    if not user_db:
        raise credentials_execption
    return user_db