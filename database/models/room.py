from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
import datetime
from .base import Base

class Room(Base):
    __tablename__ = 'rooms'
    id = Column(Integer, primary_key=True)
    key = Column(Integer, unique=True)
    user1 = Column(Integer)
    user2 = Column(Integer, nullable=True)
    # created_at = Column(DateTime, default=datetime.datetime.now())
    
    # Relationships
    # swipes = relationship('Swipe', back_populates='user')
    # matches = relationship('Match', back_populates='user')