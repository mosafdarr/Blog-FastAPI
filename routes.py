from datetime import timedelta
from fastapi import Depends, FastAPI, HTTPException, status
from logger import logger

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext

from config.auth import authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_current_active_user
from models.models import delete_posts, fetch_posts, fetch_post, initiate, insert_user, insert_posts, update_posts, user_posts
from schema.schema import PostSchema, Token, User, UserSignUp


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()
logger.info("Starting Blog APIs...")


@app.on_event("startup")
async def initiate_tables():
    logger.info("Database Populated with dummy values") if initiate() else logger.info("Already Populated")


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username/password", 
                              headers={"WWW-Authenticate": "Bearer"})
    
    logger.info("Parsing the csrf token to user")
    user = authenticate_user(form_data.username, form_data.password)

    if not user:
        raise exception

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    logger.info(f"Reading credentials of user {current_user.username}")
    return current_user


@app.get("/users/me/items")
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    logger.info(f"Reading all posts printed by {current_user.username}")
    return [{"item_id": 1, "owner": current_user}]


@app.post("/signup")
async def signup(user: UserSignUp):
    exception = HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Please enter valid data")
    logger.info(f"Creating a new user with username: {user.username}")

    if len(user.username) < 4:
        raise exception

    inserted = insert_user(user)

    if inserted:
        return { "Details": "User is created successfully!"}
    else:
        raise exception


@app.get("/posts")
async def posts(current_user: User = Depends(get_current_active_user)):
    exception = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Couldn't find any posts")
    logger.info("Displaying all posts")

    all_posts = fetch_posts()

    try:
        if all_posts:
            return {"Posts": all_posts}
    except FileNotFoundError:
        raise exception


@app.post("/insert/post")
async def insert_post(post: PostSchema, current_user: User = Depends(get_current_active_user)):
    exception = HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid format")
    logger.info(f"Inserting a new posts by user: {current_user.username}")

    inserted = insert_posts(post, current_user)

    if inserted:
        return { "Details": current_user.id, "post": post }
    else:
        raise exception


@app.get("/user/posts")
async def user_post(current_user: User = Depends(get_current_active_user)):
    exception = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with user ID: {current_user.id} does not exists")
    logger.info(f"Displaying all posts of user {current_user.username}")

    all_post = user_posts(current_user)

    if all_post:
        return all_post
    else:
        raise exception


@app.get("/search/post/{p_id}")
async def search_post(p_id: int, current_user: User = Depends(get_current_active_user)):
    exception = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with ID: {p_id} does not exists")
    logger.info(f"Searching for a post with post ID {p_id}")

    post = fetch_post(p_id)

    if post:
        return {"Post": post}
    else:
        raise exception


@app.put("/update/post/{p_id}")
async def update_post(p_id: int, post: PostSchema, current_user: User = Depends(get_current_active_user)):
    logger.info(f"Updating a post with post ID {p_id}")
    exception = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with ID: {p_id} does not exists")

    updated = update_posts(p_id, post, current_user)

    if updated:
        return { "Status": "Post Updated Successfully" }
    else:
        raise exception


@app.delete("/delete/post/{p_id}")
async def delete_post(p_id: int, current_user: User = Depends(get_current_active_user)):
    exception = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with ID: {p_id} does not exists")
    logger.info(f"deleting a post with post ID {p_id}")

    deleted = delete_posts(p_id)

    if deleted:
        return {"status": "Post Deleted Successfully"}
    else:
        raise exception
