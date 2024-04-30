from sqlalchemy import Column, Integer, Boolean
from sqlalchemy.orm import relationship
from .base import Base

class Match(Base):
    __tablename__ = 'matches'
    id = Column(Integer, primary_key=True)
    room_id = Column(Integer)
    film_id = Column(Integer)
    user1_vote = Column(Boolean, nullable=True)
    user2_vote = Column(Boolean, nullable=True)