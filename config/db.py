from sqlalchemy import create_engine

from sqlalchemy.orm import declarative_base, sessionmaker


engine = create_engine("postgresql://postgres:safdarm@localhost:5432/Blogs", echo=False)

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()
