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
        blog_content["created_at"] = str(datetime.now(timezone.utc))
        blog_content["status"] = blog_content["delete_status"] = False

        new_blog_content = await db["blogPost"].insert_one(blog_content)

        created_blog_post = await db["blogPost"].find_one({"_id" : new_blog_content.inserted_id})

        return created_blog_post

    except Exception as e :
        print(e)
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )

# Publish a blog
@router.put("/publish/{id}", response_description = "Publish blog content", response_model = BlogContentResponse)
async def publish_blog(id : str, current_user = Depends(oauth2.get_current_user)):

    if blog_post := await db["blogPost"].find_one({"_id" : id, "delete_status" : False}) :

        if blog_post["author_id"] == current_user["_id"] :

            try :

                # Get current time
                timestamp = {"published_at" : datetime.today()}
                post_status = {"status" : True}

                # Change data in JSON
                json_timestamp = jsonable_encoder(timestamp)
                json_post_status = jsonable_encoder(post_status)

                # Merging JSON objects
                blog_post = {**blog_post, **json_timestamp, **json_post_status}

                update_result = await db["blogPost"].update_one({"_id" : id}, {"$set" : blog_post})

                if update_result.modified_count == 1 :

                    if (updated_blog_post := await db["blogPost"].find_one({"_id" : id })) is not None :

                        return updated_blog_post

                if (existing_blog_post := await db["blogPost"].find_one({"_id" : id})) is not None :

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
    
# Publish a blog
@router.put("/unpublish/{id}", response_description = "Publish blog content", response_model = BlogContentResponse)
async def unpublish_blog(id : str, current_user = Depends(oauth2.get_current_user)):

    if blog_post := await db["blogPost"].find_one({"_id" : id, "delete_status" : False}) :

        if blog_post["author_id"] == current_user["_id"] :

            if blog_post["status"] == False :

                raise HTTPException(
                    status_code = status.HTTP_304_NOT_MODIFIED,
                    detail = "Blog post is already published"
                )
            
            elif blog_post["status"] == True :

                try :

                    # Get current time
                    timestamp = {"unpublished_at" : datetime.today()}
                    post_status = {"status" : False}

                    # Change data in JSON
                    json_timestamp = jsonable_encoder(timestamp)
                    json_post_status = jsonable_encoder(post_status)

                    # Merging JSON objects
                    blog_post = {**blog_post, **json_timestamp, **json_post_status}

                    update_result = await db["blogPost"].update_one({"_id" : id}, {"$set" : blog_post})

                    if update_result.modified_count == 1 :

                        if (updated_blog_post := await db["blogPost"].find_one({"_id" : id })) is not None :

                            return updated_blog_post

                    if (existing_blog_post := await db["blogPost"].find_one({"_id" : id})) is not None :

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

# Get all deleted posts limit to 10 per page and order by created date by user
@router.get("/all_deleted", response_description = "Get deleted blogs content", response_model = List[BlogContentResponse])
async def get_deleted_blogs(limit : int = 10, order_by : str = "deleted_at", current_user = Depends(oauth2.get_current_user)):

    try :

        if blog_posts := await db["blogPost"].find({"delete_status" : True}).sort(order_by, -1).to_list(limit) :

            result = []

            for post in blog_posts:

                if post["author_id"] == current_user["_id"]:

                    author_details = await db["users"].find_one({"_id": post["author_id"]})
                    post["author"] = author_details

                    result.append(post)
                else:

                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="You cannot access posts that you do not own."
                    )

            return result
            
        else :

            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail = "Internal server error"
            )
        
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
        blog_posts = await db["blogPost"].find({"status" : True, "delete_status" : False}).sort(order_by, -1).to_list(limit)

        return blog_posts
    
    except Exception as e :
        print(e)
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )
    
# Get all unpublished posts limit to 10 per page and order by created date by user
@router.get("/unpublished", response_description = "Get unpublished blogs content", response_model = List[BlogContentResponse])
async def get_unpublished_blogs(limit : int = 10, order_by : str = "created_at", current_user = Depends(oauth2.get_current_user)):

    if blog_posts := await db["blogPost"].find({"status": False, "delete_status" : False}).sort(order_by, -1).to_list(limit) :

        result = []
    
        for post in blog_posts:

            if post["author_id"] == current_user["_id"]:
                
                author_details = await db["users"].find_one({"_id": post["author_id"]})
                post["author"] = author_details
                
                result.append(post)
            else:

                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="You cannot access posts that you do not own."
                )

        return result
        
    else :

        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )
        
# Get one blog
@router.get("/{id}", response_description = "Get blog content", response_model = BlogContentResponse)
async def get_blog(id : str):

    try :
        blog_post = await db["blogPost"].find_one({"_id" : id, "status" : True, "delete_status" : False})

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

    if blog_post := await db["blogPost"].find_one({"_id" : id, "delete_status" : False}) :

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

                    if (existing_blog_post := await db["blogPost"].find_one({"_id" : id})) is not None :

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
    
# Soft Delete of a blog post
@router.put("/delete/{id}", response_description = "Delete blog content")
async def delete_blog(id : str, current_user = Depends(oauth2.get_current_user)):

    if blog_post := await db["blogPost"].find_one({"_id" : id, "delete_status" : False}) :

        if blog_post["author_id"] == current_user["_id"] :

            if blog_post["delete_status"] == True :

                raise HTTPException(
                    status_code = status.HTTP_304_NOT_MODIFIED,
                    detail = "Blog post is already deleted"
                )
            
            elif blog_post["delete_status"] == False :

                try :

                    # Get current time
                    timestamp = {"deleted_at" : datetime.today()}
                    post_status = {"delete_status" : True}

                    # Change data in JSON
                    json_timestamp = jsonable_encoder(timestamp)
                    json_post_status = jsonable_encoder(post_status)

                    # Merging JSON objects
                    blog_post = {**blog_post, **json_timestamp, **json_post_status}

                    update_result = await db["blogPost"].update_one({"_id" : id}, {"$set" : blog_post})

                    if update_result.modified_count == 1 :

                        if (updated_blog_post := await db["blogPost"].find_one({"_id" : id })) is not None :

                            return updated_blog_post

                    if (existing_blog_post := await db["blogPost"].find_one({"_id" : id})) is not None :

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

# Hard Delete a blog
@router.delete("/hard_delete/{id}", response_description = "Hard Delete blog content")
async def hard_delete_blog_post(id : str, current_user = Depends(oauth2.get_current_user)):
    
    if blog_post := await db["blogPost"].find_one({"_id" : id}) :

        if blog_post["author_id"] == current_user["_id"]:

            try :

                delete_result = await db["blogPost"].delete_one({"_id" : id})
                
                if delete_result.deleted_count == 1 :
                    
                    return HTTPException(
                        status_code = status.HTTP_204_NO_CONTENT,
                    )
                
                raise HTTPException(
                    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail = "Internal server error"
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
