from sqlalchemy import Column, Integer, String

from sqlalchemy.orm import relationship

from config.db import get_base


class User(get_base()):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(20), nullable=False)
    email = Column(String, nullable=False)
    password = Column(String(60), nullable=False)

    posts = relationship("Post", back_populates="user")
