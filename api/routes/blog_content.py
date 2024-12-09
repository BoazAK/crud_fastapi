from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from api.schemas import BlogContent, BlogContentResponse, db
from api import oauth2
from datetime import datetime, timezone
from typing import List

router = APIRouter(
    prefix = "/blog",
    tags = ["Blog Content"]
)

# Create blog
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
    
# Get all posts limit to 10 per page and order by created date
@router.get("", response_description = "Get blogs content", response_model = List[BlogContentResponse])
async def get_blogs(limit : int = 10, order_by : str = "created_at"):

    try :
        blog_posts = await db["blogPost"].find({"$query" : {}, "$orderby" : {order_by : -1}}).to_list(limit)

        return blog_posts
    
    except Exception as e :
        print(e)
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )
    
# Get one blog
@router.get("/{id}", response_description = "Get blog content", response_model = BlogContentResponse)
async def get_blog(id : str):

    try :
        blog_post = await db["blogPost"].find_one({"_id" : id})

        if blog_post is None :

            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "Blog with this ID not found"
            )

        return blog_post
    
    except Exception as e :
        print(e)
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )
    
# Update a blog
@router.put("/{id}", response_description = "Update blog content", response_model = BlogContentResponse)
async def update_blog(id : str, blog_content : BlogContent, current_user = Depends(oauth2.get_current_user)):
    if blog_post := await db["blogPost"].find_one({"_id" : id}) :
        if blog_post["author_id"] == current_user["_id"] :
            try :
                blog_content = {k : v for k, v in blog_content.model_dump().items() if v is not None}

                if len(blog_content) >=1 :

                    # Get current time
                    timestamp = {"updated_at" : datetime.today()}

                    # Change data in JSON
                    json_timestamp = jsonable_encoder(timestamp)

                    # Merging JSON objects
                    blog_content = {**blog_content, **json_timestamp}

                    update_result = await db["blogPost"].update_one({"_id" : id}, {"$set" : blog_content})

                    if update_result.modified_count == 1 :

                        if (updated_blog_post := await db["blogPost"].find_one({"_id" : id })) is not None :

                            return updated_blog_post

                    if (existing_blog_post := await db["blogPost"].findo_one({"_id" : id})) is not None :

                        return existing_blog_post
                    
                    raise HTTPException(
                        status_code = status.HTTP_404_NOT_FOUND,
                        detal = "Blog with this ID not found"
                    )
            
            except Exception as e :
                print(e)
                raise HTTPException(
                    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail = "Internal server error"
                )
            
        else :
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "You are not the author of this blog post"
            )
        
    else :
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Blog with this ID not found"
        )
