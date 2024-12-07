from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder
from ..schemas import User, db, UserResponse
from ..utils import get_password_hash
from datetime import datetime

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

def read_root():
    content = {"timestamp": datetime.now()}
    json_compatible_content = jsonable_encoder(content)
    return json_compatible_content


@router.post("/registration", response_description = "Register a user", response_model = UserResponse)
async def registration(user_info: User):

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

    # Send the email to the user
    
    return created_user
