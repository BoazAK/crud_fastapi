import jwt
from jwt.exceptions import InvalidTokenError
from datetime import date, datetime, timedelta, timezone
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

def create_access_token(payload : dict):
    to_encode = payload.copy()

    expiration_time = datetime.now(timezone.utc) + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES )

    to_encode.update({"exp" : expiration_time})

    jwt_token = jwt.encode(to_encode, key = SECRET_KEY, algorithm = ALGORITHM)

    return jwt_token


