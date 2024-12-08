from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError, validate_call
from ..schemas import User, db, UserResponse
from ..utils import get_password_hash
from datetime import datetime
from ..send_email import send_registration_email

import secrets

router = APIRouter(
    tags = ["User Routes"]
)

@router.get("/")
def get():
    return {
        "status": "OK",
        "message": "Hello World"
    }

@router.post("/registration", response_description = "Register a user", response_model = UserResponse)
async def registration(user_info: User):
    # Get current time
    timestamp = {"created_at": datetime.now(), "updated_at": datetime.now()}

    # Change data in JSON
    json_timestamp = jsonable_encoder(timestamp)
    user_info = jsonable_encoder(user_info)

    # Merging JSON objects
    user_info = {**user_info, **json_timestamp}

    # Check for duplication
    username_found = await db["users"].find_one({"name": user_info["name"]})
    email_found = await db["users"].find_one({"email": user_info["email"]})

    if username_found:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = "Username is already taken"
        )
    
    if email_found:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = "Email is already taken"
        )
    
    # Hash user's passowrd
    user_info["password"] = get_password_hash(user_info["password"])

    # Create API Key
    user_info["apiKey"] = secrets.token_hex(30)

    # Save the user
    new_user = await db["users"].insert_one(user_info)
    created_user = await db["users"].find_one({"_id" : new_user.inserted_id})

    await send_registration_email("Registratoin successful", user_info["email"], {
        "title" : "Registration Successfuly",
        "name" : user_info["name"]
    })
    
    return created_user
