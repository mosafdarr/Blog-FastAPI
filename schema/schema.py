from pydantic import BaseModel
from pydantic import EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str or None = None


class User(BaseModel):
    username: str
    email: str or None = None
    disabled: bool or None = None


class UserInDB(User):
    hashed_password: str


class UserSignUp(BaseModel):
    username: str
    email: EmailStr
    password: str


class PostSchema(BaseModel):
    title: str
    content: str
