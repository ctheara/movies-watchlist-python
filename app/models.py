from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    imdb_id = Column(String, unique=True, index=True, nullable=True)
    title = Column(String, index=True, nullable=True)
    year = Column(String, nullable=True)
    genre = Column(String, nullable=True)
    rating = Column(String, nullable=True)
    plot = Column(String, nullable=True)
    poster_url = Column(String, nullable=True)
    watched = Column(Boolean, default=False)
    date_added = Column(String, nullable=True)
