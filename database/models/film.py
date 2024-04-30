from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
import datetime
from .base import Base

class Film(Base):
    __tablename__ = 'films'
    id = Column(Integer, primary_key=True)
    kpid = Column(Integer, unique=True)
    name = Column(String)
    description = Column(String)
    image = Column(String)
    rating_kp = Column(Float)
    rating_imdb = Column(Float)
    genre = Column(String)
    
    # Relationships
    # swipes = relationship('Swipe', back_populates='user')
    # matches = relationship('Match', back_populates='user')