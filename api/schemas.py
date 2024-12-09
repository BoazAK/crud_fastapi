import motor.motor_asyncio
from dotenv import load_dotenv
from bson import ObjectId
from typing import Any, Dict
from pydantic_core import CoreSchema
from pydantic import BaseModel, Field, EmailStr, GetJsonSchemaHandler, field_validator
from uuid import uuid4
import os, re

# Load env
load_dotenv()

# Connection to MongoDB database
client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGODB_URL"))

# Create simple collection
db = client.blog_api

class User(BaseModel):
    id: str = Field(default_factory = lambda: uuid4().hex, alias = "_id")
    name: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)

    @field_validator('name')
    @classmethod
    def name_check(cls, v: str) -> str :
        # Name validation
        # if not v or len(v) < 6 or " " in v :
        if not v or len(v) < 6 :
            raise ValueError("Name length can't be under 6 characters")
            # raise ValueError("Name length can't be under 6 characters or can't contain a space")
        
        return v
    
    @field_validator('email')
    @classmethod
    def email_check(cls, v: str) -> str :
        # Regex for email validation
        regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        # Check if the email is correct according to the regex
        if not v or not re.match(regex, v):
            raise ValueError("Email format is not valid")
        
        return v
    
    @field_validator('password')
    @classmethod
    def password_check(cls, v: str) -> str :
        # Password length validation
        if not v or len(v) < 8 :
            raise ValueError("Password length can't be under 8 characters")
        
       # Check if password contain at least one uppercase letter, one lowercase letter, one number and one special character.
        if not re.search(r'[A-Z]', v) and not re.search(r'[a-z]', v) and not re.search(r'[0-9]', v) and not re.search(r'[@$!%*?&]', v):
            raise ValueError("Password must contain at least one uppercase letter, one lowercase letter, one number and one special character.")

        return v
    
    class Config:
        allowed_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example" : {
                "name": "John Doe",
                "email": "jdoe@example.com",
                "password": "s3cRet_password"
            }
        }

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> Dict[str, Any]:
        json_schema = super().__get_pydantic_json_schema__(core_schema, handler)
        json_schema = handler.resolve_ref_schema(json_schema)
        json_schema.update(type = "string")
        
        return json_schema

class UserResponse(BaseModel):
    id: str = Field(default_factory = lambda: uuid4().hex, alias = "_id")
    name: str = Field(...)
    email: EmailStr = Field(...)
    
    class Config:
        allowed_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example" : {
                "name": "John Doe",
                "email": "jdoe@example.com"
            }
        }

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> Dict[str, Any]:
        json_schema = super().__get_pydantic_json_schema__(core_schema, handler)
        json_schema = handler.resolve_ref_schema(json_schema)
        json_schema.update(type = "string")
        
        return json_schema
    
class BlogContent(BaseModel):
    id: str = Field(default_factory = lambda: uuid4().hex, alias = "_id")
    title : str = Field(...)
    body : str = Field(...)

    class Config :
        allowed_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example" : {
                "title": "Blog title",
                "body": "Blog content"
            }
        }

class BlogContentResponse(BaseModel):
    id: str = Field(default_factory = lambda: uuid4().hex, alias = "_id")
    title : str = Field(...)
    body : str = Field(...)
    status : bool
    author_name : str = Field(...)
    author_id : str = Field(...)
    created_at : str = Field(...)
    updated_at : str = Field(...)

    class Config :
        allowed_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example" : {
                "title": "Blog title",
                "body": "Blog content",
                "status" : "Blog published status",
                "author_name" : "Name of the author",
                "author_id" : "ID of the author",
                "created_at" : "Date blog created",
                "published_at" : "Date blog published",
                "unpublished_at" : "Date blog unpublished",
                "updated_at" : "Date blog updated"
            }
        }
    
class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    id : str

class PasswordReset(BaseModel):
    email : EmailStr = Field(...)

class NewPassword(BaseModel):
    password : str = Field(...)
    