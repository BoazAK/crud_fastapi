from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidTokenError
from datetime import date, datetime, timedelta, timezone
from dotenv import load_dotenv
import os

from api.schemas import db, TokenData

load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "login")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

def create_access_token(payload : dict) :
    to_encode = payload.copy()

    expiration_time = datetime.now(timezone.utc) + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES )

    to_encode.update({"exp" : expiration_time})

    jwt_token = jwt.encode(to_encode, key = SECRET_KEY, algorithm = ALGORITHM)

    return jwt_token

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) :
    credentials_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "Could not validate token",
        headers = {"WWW-Authenticate": "Bearer"},
    )
        
    try :
        payload = jwt.decode(token, key = SECRET_KEY, algorithms = ALGORITHM)
        user_id : str = payload.get("_id")
        if not user_id : # Same as if user_id is None
            raise credentials_exception
        
        token_data = TokenData(id=user_id)

    except InvalidTokenError :
        raise credentials_exception
    
    current_user = await db["user"].find_one({"_id" : token_data.id})

    if current_user is None :
        raise credentials_exception
    
    return current_user
