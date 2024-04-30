from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
import datetime
from .base import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True)
    username = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.datetime.now())
    
    # Relationships
    # swipes = relationship('Swipe', back_populates='user')
    # matches = relationship('Match', back_populates='user')