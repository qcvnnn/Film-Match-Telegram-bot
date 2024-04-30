from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models.base import Base

engine = create_engine('sqlite:///database.db')  # Adjust for your database

Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(engine)
