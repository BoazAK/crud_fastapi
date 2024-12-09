from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from api.schemas import BlogContent, BlogContentResponse, db
from api import oauth2
from datetime import datetime, timezone

router = APIRouter(
    prefix = "/blog",
    tags = ["Blog Content"]
)

@router.post("", response_description = "Create blog content", response_model = BlogContentResponse)
async def create_blog(blog_content : BlogContent, current_user = Depends(oauth2.get_current_user)):
    try :
        blog_content = jsonable_encoder(blog_content)

        # Add additional informations
        blog_content["author_name"] = current_user["name"]
        blog_content["author_id"] = current_user["_id"]
        blog_content["created_at"] = blog_content["updated_at"] = str(datetime.now(timezone.utc))

        new_blog_content = await db["blogPost"].insert_one(blog_content)

        created_blog_post = await db["blogPost"].find_one({"_id" : new_blog_content.inserted_id})

        return created_blog_post

    except Exception as e :
        print(e)
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )
