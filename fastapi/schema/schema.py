from pydantic import BaseModel, EmailStr, validator


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

    @validator("username")
    @classmethod
    def username_must_have_3_letters(cls, username: str):
        if len(username) < 3:
            raise ValueError("Username must contain at least three letters")
        
        return username.title()

    @validator("password")
    @classmethod
    def password_must_have_3_letters(cls, password: str):
        if len(password) < 3: 
            raise ValueError("Password must be strong")
        
        return password.title()



class PostSchema(BaseModel):
    title: str
    content: str
