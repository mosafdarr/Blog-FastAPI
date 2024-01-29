from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from sqlalchemy.orm import relationship, backref

from config.db import get_base


class Post(get_base()):
    __tablename__ = "post"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    date_posted = Column(DateTime, nullable=False)
    content = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    user = relationship("User", backref=backref("post"))
