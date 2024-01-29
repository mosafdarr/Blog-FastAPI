from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, inspect
from sqlalchemy.orm import relationship
from config.db import Base, session, engine
from config.auth import get_password_hash
from schema.schema import UserSignUp, PostSchema


class Posts(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, nullable=False)
    date_posted = Column(DateTime, nullable=False, default=datetime.now())
    content = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))

    users = relationship("Users", back_populates="posts")


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(20), nullable=False)
    email = Column(String, nullable=False)
    hashed_password = Column(String(60), nullable=False)
    disabled = Column(Boolean, default=False)

    posts = relationship("Posts", back_populates="users")


def initiate():
    flag = False
    test_user = Users(username="Safdar", email="mosafdarlalii@gmail.com",
                     hashed_password="$2b$12$grKVbhOmHvUz/iyG/fz5LOyVBoeyCwNzTYnkk6y7D.SWDq9tBEm6e")

    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(tables)

    if "users" not in tables:
        Users.__table__.create(bind=engine)
        session.add(test_user)
        session.commit()

        flag = True

    if "posts" not in tables:
        Posts.__table__.create(bind=engine)
        post1 = Posts(title="Man must explore, and this is exploration at its greatest",
                     content="Science cuts two ways, of course; its products can be used for both good and evil.\
                              But there's no turning back from science. The early warnings about technological \
                              dangers also come from science.",
                     user_id=test_user.id)
        post2 = Posts(title="Science has not yet mastered prophecy",
                     content="Science cuts two ways, of course; its products can be used for both good and evil.\
                                      But there's no turning back from science. The early warnings about technological \
                                      dangers also come from science.",
                     user_id=test_user.id)
        post3 = Posts(title="Problems look mighty small from 500 miles up",
                     content="Science cuts two ways, of course; its products can be used for both good and evil.\
                                      But there's no turning back from science. The early warnings about technological \
                                      dangers also come from science.",
                     user_id=test_user.id)

        session.add_all([post1, post2, post3])
        session.commit()

        flag = True

    return flag


def fetch_posts():
    posts = session.query(Posts).all()
    return posts


def insert_user(user: UserSignUp):
    try:
        temp_user = session.query(Users).filter_by(username=user.username, email=user.email).first()

        if temp_user:
            return False

        temp_user = Users(username=user.username, email=user.email, hashed_password=get_password_hash(user.password))
        session.add(temp_user)
        session.commit()

        return True

    except Exception:
        return False


def insert_posts(post: PostSchema, current_user):
    try:
        temp_post = Posts(title=post.title, content=post.content, user_id=current_user.id)

        session.add(temp_post)
        session.commit()

        return True

    except Exception:
        return False


def user_posts(current_user):
    posts = session.query(Posts).filter_by(user_id=current_user.id).all()

    if posts:
        return posts

    return False


def fetch_post(post_id):
    try:
        post = session.query(Posts).filter_by(id=post_id).first()
        print("model, True")
        return post

    except Exception:
        print("model, False")
        return False


def update_posts(post_id, post, current_user):
    try:
        temp_post = session.query(Posts).filter_by(id=post_id).first()
        temp_post.title = post.title
        temp_post.content = post.content
        temp_post.user_id = current_user.id
        temp_post.date_posted = datetime.now()

        session.commit()
        return True

    except Exception:
        return False


def delete_posts(post_id):
    try:
        post = session.query(Posts).filter_by(id=post_id).first()
        session.delete(post)
        session.commit()
        return True
    except Exception:
        return False

