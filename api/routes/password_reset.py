import datetime
from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder
from api.schemas import UserResponse, db, NewPassword, PasswordReset
from api.oauth2 import create_access_token, get_current_user
from api.send_email import password_reset, password_changed
from api.utils import get_password_hash

router = APIRouter(
    prefix = "/password",
    tags = ["Password reset"]
)

@router.post("", response_description = "Password reset request")
async def reset_request(user_email : PasswordReset) :
    user = await db["users"].find_one({"email" : user_email.email})

    if user is not None :
        token = create_access_token({"id" : user["_id"]}, 5)

        # Local link for password reset
        reset_link = f"http://127.0.0.1:8000/?token={token}"

        # On line link for password reset
        # reset_link = f"https://domain.name/?token={token}"

        # Send Email to the user
        await password_reset(
            "Password reset",
            user["email"],
            {
                "title" : "Password reset",
                "name" : user["name"],
                "reset_link" : reset_link
            }
        )
    
    else:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "User with this email not found"
        )
    
@router.put("", response_description = "Password reset", response_model = UserResponse)
async def reset(token : str, new_password : NewPassword) :
    # Pass all the data into dictionary
    request_data = {k : v for k, v in new_password.model_dump().items() if v is not None}

    # Replace the clear password with the hashed one
    request_data["password"] = get_password_hash(request_data["password"])

    # Check if the length of the request is greater than 1
    if len(request_data) >= 1 :
        # Get current user from the token
        user = await get_current_user(token)

        # Get current time
        timestamp = {"last_pwd_changed_date" : datetime.datetime.today()}
        
        # Change data in JSON
        json_timestamp = jsonable_encoder(timestamp)

        # Merging JSON objects
        request_data = {**request_data, **json_timestamp}

        # Update the user's informations with the password get by the field
        update_result = await db["users"].update_one(
            {"_id" : user["_id"]},
            {"$set" : request_data}
        )

        # Get the currently user updated
        if update_result.modified_count == 1 :
            updated_user = await db["users"].find_one({"_id" : user["_id"]})

            if updated_user is not None :

                # Local link for login
                login_link = f"http://127.0.0.1:8000/login"

                # On line link for login
                # login_link = f"https://domain.name/login"
                
                # Send email to the user after password reset
                await password_changed(
                    "Password changed",
                    user["email"],
                    {
                        "title" : "Password changed",
                        "name" : user["name"],
                        "login_link" : login_link
                    }
                )

                return updated_user

    # If nothing is provided, take the existing user
    existing_user = await db["users"].find_one({"_id" : user["_id"]})

    if existing_user is not None :
        return existing_user
    
    raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND,
        detail = "User with this email not found"
    )
