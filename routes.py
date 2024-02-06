import secrets

from datetime import timedelta
from fastapi import Depends, FastAPI, HTTPException, status, UploadFile
from logger import logger, error_logger
from os import path
from PIL import Image

from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext

from config.auth import authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_current_active_user
from config.db import session
from models.models import delete_posts, fetch_posts, fetch_post, initiate, insert_user, insert_posts, save_picture, update_posts, user_posts
from schema.schema import PostSchema, Token, User, UserSignUp


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()
logger.info("Starting Blog APIs...")


@app.on_event("startup")
async def initiate_tables():
    if initiate():
        logger.info("Database Populated with dummy values") 


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint to generate access token for user login.
    
    Args:
        form_data (OAuth2PasswordRequestForm): Form data containing username and password.

    Returns:
        Token: Access token.
    """

    exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username/password", 
                              headers={"WWW-Authenticate": "Bearer"})
    
    logger.info("Parsing the csrf token to user")
    user = authenticate_user(form_data.username, form_data.password)

    if not user:
        error_logger.error("User is trying to login but is not authenticated.")
        raise exception

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users-me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Endpoint to read user details.

    Args:
        current_user (User): Current authenticated user.

    Returns:
        User: User details.
    """

    logger.info(f"Reading credentials of user {current_user.username}")
    return current_user


@app.get("/users-items")
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    """
    Get all items owned by the current user.

    Args:
        current_user (User): Current authenticated user.

    Returns:
        list: List of items owned by the current user.
    """

    logger.info(f"Reading all posts printed by {current_user.username}")
    return [{"item_id": 1, "owner": current_user}]


@app.post("/signup")
async def signup(user: UserSignUp):
    """
    Create a new user.

    Args:
        user (UserSignUp): User details from the signup form.

    Returns:
        dict: Details of the created user.
        
    Raises:
        HTTPException: If unable to create a user.
    """

    exception = HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Either user already exist or you're entering a wrong data")

    inserted = insert_user(user)

    if inserted:
        logger.info(f"Creating a new user with username: {user.username}")
        return { "Details": "User is created successfully!"}

    error_logger.error("Unable to create a user.")
    raise exception


@app.get("/posts")
async def posts(current_user: User = Depends(get_current_active_user)):
    """
    Get all posts.

    Args:
        current_user (User): Current authenticated user.

    Returns:
        dict: Details of all posts.
        
    Raises:
        HTTPException: If no posts are found.
    """

    exception = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Couldn't find any posts")

    all_posts = fetch_posts()

    try:
        if all_posts:
            logger.info("Displaying all posts")
            return {"Posts": all_posts}
        
    except FileNotFoundError:
        error_logger.error("Couldn't fetch any posts from database")
        raise exception


@app.post("/insert-post")
async def insert_post(post: PostSchema, current_user: User = Depends(get_current_active_user)):
    """
    Insert a new post.

    Args:
        post (PostSchema): Details of the new post.
        current_user (User): Current authenticated user.

    Returns:
        dict: Details of the inserted post.
        
    Raises:
        HTTPException: If the post format is invalid or insertion fails.
    """

    exception = HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid format")

    inserted = insert_posts(post, current_user)

    if inserted:
        logger.info(f"Inserting a new posts by user: {current_user.username}")
        return { "Details": current_user.id, "post": post }
 
    error_logger.error("Coulnt insert a new post")
    raise exception


@app.get("/user-posts")
async def user_post(current_user: User = Depends(get_current_active_user)):
    """
    Get all posts associated with the current user.

    Args:
        current_user (User): Current authenticated user.

    Returns:
        dict: All posts of the current user.
        
    Raises:
        HTTPException: If no posts are found for the current user.
    """

    exception = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with user ID: {current_user.id} does not exists")

    all_post = user_posts(current_user)

    if all_post:
        logger.info(f"Displaying all posts of user {current_user.username}")
        return all_post
    
    error_logger.error(f"Couldn't fine any user with username {current_user.username}")
    raise exception


@app.get("/search-post/{p_id}")
async def search_post(p_id: int, current_user: User = Depends(get_current_active_user)):
    """
    Search for a post by post ID.

    Args:
        p_id (int): Post ID to search.
        current_user (User): Current authenticated user.

    Returns:
        dict: Details of the searched post.
        
    Raises:
        HTTPException: If the post with the given ID is not found.
    """

    exception = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post does not exists")

    post = fetch_post(p_id)

    if post:
        logger.info(f"Searching for a post with post ID {p_id}")
        return {"Post": post}
    
    error_logger.error(f"Couldn't search any post with post ID {p_id}")
    raise exception


@app.put("/update-post/{p_id}")
async def update_post(p_id: int, post: PostSchema, current_user: User = Depends(get_current_active_user)):
    """
    Update a post by post ID.

    Args:
        p_id (int): Post ID to update.
        post (PostSchema): Updated post details.
        current_user (User): Current authenticated user.

    Returns:
        dict: Details of the updated post.
        
    Raises:
        HTTPException: If the post with the given ID is not found.
    """

    exception = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post does not exists")

    updated = update_posts(p_id, post, current_user)

    if updated:
        logger.info(f"Updating a post with post ID {p_id}")
        return { "Status": "Post Updated Successfully" }
    
    error_logger.error(f"Couldn't Find any post with ID {p_id} to update")
    raise exception


@app.delete("/delete-post/{p_id}")
async def delete_post(p_id: int, current_user: User = Depends(get_current_active_user)):
    """
    Delete a post by post ID.

    Args:
        p_id (int): Post ID to delete.
        current_user (User): Current authenticated user.

    Returns:
        dict: Details of the deleted post.
        
    Raises:
        HTTPException: If the post with the given ID is not found.
    """

    exception = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Either post doesn't exist or you dont have the right access to delete this post")

    deleted = delete_posts(p_id, current_user.id)

    if deleted:
        logger.info(f"deleting a post with post ID {p_id}")
        return {"status": "Post Deleted Successfully"}

    error_logger.error(f"Unable to delete a post with post ID {p_id}")
    raise exception


@app.post("/upload-file")
async def create_upload_file(file: UploadFile):
    """
    Upload a file.

    Args:
        file (UploadFile): Uploaded file.

    Returns:
        dict: Details of the uploaded file.
    """
     
    random_hex = secrets.token_hex(8)

    _, f_ext = path.splitext(file.filename)
    picture_fn = random_hex + f_ext
    picture_path = path.join(app.root_path, 'static/posts', picture_fn)

    output_size = (150,150) 
    i = Image.open(file.file)
    i.thumbnail(output_size)
    i.save(picture_path)

    save_picture(picture_fn)
    return {"Details": "Picture Successfully Uploaded"}
