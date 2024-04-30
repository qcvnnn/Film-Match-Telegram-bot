from sqlalchemy.orm import declarative_base

Base = declarative_base()

from database.models import user, film, room, match