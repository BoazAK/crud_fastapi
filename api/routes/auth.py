from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from api.schemas import db
from api import utils
from api.oauth2 import create_access_token

router = APIRouter(
    prefix = "/login",
    tags = ["Authentication"]
)

@router.post("", status_code = status.HTTP_200_OK)
async def login(user_credentials: OAuth2PasswordRequestForm = Depends()) :
    # Find one user by username or by email
    user = await db["users"].find_one({
        "$or": [
            {"name": user_credentials.username},
            {"email": user_credentials.username}
        ]
    })

    # Validate user credentials and create access token
    if user and utils.verify_password(user_credentials.password, user["password"]):
        # Create the access token
        access_token = create_access_token({"id": user["_id"]})

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    
    else :
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "Invalid user credentials",
            headers = {"WWW-Authenticate": "Bearer"},
        )
