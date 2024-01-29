from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from passlib.context import CryptContext

from models.models import (initiate, fetch_posts, insert_user, insert_posts, user_posts,
                           fetch_post, update_posts, delete_posts)
from schema.schema import Token, User, UserSignUp, PostSchema
from config.auth import authenticate_user, create_access_token, get_current_active_user, ACCESS_TOKEN_EXPIRE_MINUTES

from logger import logger

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()
logger.info("Starting Blog APIs...")


@app.on_event("startup")
async def initiate_tables():
    logger.info("Populating Database")
    print("Database populated with tables") if initiate() else print("Database not initiated or Already initiated")


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    logger.info("Parsing the csrf token to user")
    user = authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})

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
    logger.info(f"Creating a new user with username: {user.username}")
    exception = HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Please enter valid data")

    if len(user.username) < 4:
        raise exception

    if insert_user(user):
        return {
                "Details": "User is created successfully!"
            }

    raise exception


@app.get("/posts")
async def posts(current_user: User = Depends(get_current_active_user)):
    logger.info("Displaying all posts")
    exception = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Couldn't find any posts")

    all_posts = fetch_posts()

    try:
        if all_posts:
            return {"Posts": all_posts}

    except FileNotFoundError:
        raise exception


@app.post("/insert/post")
async def insert_post(post: PostSchema, current_user: User = Depends(get_current_active_user)):
    logger.info(f"Inserting a new posts by user: {current_user.username}")
    exception = HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                   detail="Please insert again with valid format")
    inserted = insert_posts(post, current_user)

    if inserted is not False:
        return {
            "Details": current_user.id,
            "post": post
        }

    raise exception


@app.get("/user/posts")
async def user_post(current_user: User = Depends(get_current_active_user)):
    logger.info(f"Displaying all posts of user {current_user.username}")
    user_exception = HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                   detail=f"Couldn't find any posts for user with ID: {current_user.id}")
    data = user_posts(current_user)

    if data:
        return data

    raise user_exception


@app.get("/search/post/{p_id}")
async def search_post(p_id: int, current_user: User = Depends(get_current_active_user)):
    logger.info(f"Searching for a post with post ID {p_id}")
    exception = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Couldn't find any posts with ID: {p_id}")
    post = fetch_post(p_id)

    if post:
        return {"Post": post}

    raise exception


@app.put("/update/post/{p_id}")
async def update_post(p_id: int, post: PostSchema, current_user: User = Depends(get_current_active_user)):
    logger.info(f"Updating a post with post ID {p_id}")
    post_exception = HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                   detail=f"Couldn't find any posts with ID: {p_id}")
    updated = update_posts(p_id, post, current_user)

    if updated is not False:
        return {
            "Status": "Post Updated Successfully"
        }

    raise post_exception


@app.delete("/delete/post/{p_id}")
async def delete_post(p_id: int, current_user: User = Depends(get_current_active_user)):
    logger.info(f"deleting a post with post ID {p_id}")
    exception = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Couldn't find any posts with ID: {p_id}")
    res = delete_posts(p_id)

    if res is not False:
        return {"status": "Post Deleted Successfully"}

    raise exception


# @app.websocket("/posts")
# async def posts(websocket: WebSocket, current_user: User = Depends(get_current_active_user)):
#     await websocket.accept()
#
#     while True:
#         data = fetch_posts()
#         await websocket.send_json(data)
