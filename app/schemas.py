from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Incoming POST request
class MovieCreate(BaseModel):
    imdb_id: str

# Response model for getting movie details
class MovieResponse(BaseModel):
    imdb_id: str
    title: str
    year: str
    genre: Optional[str] = None
    rating: Optional[float] = None
    plot: Optional[str] = None
    poster_url: Optional[str] = None
    watched: bool
    date_added: Optional[datetime] = None

    class Config:
        orm_mode = True

# Response model for updating watched status
class MovieWatchedResponse(BaseModel):
    imdb_id: str
    title: str
    watched: bool

    class Config:
        orm_mode = True

# Response model for analytics
class AnalyticsResponse(BaseModel):
    average_rating: Optional[float] = None
    most_frequent_genre: Optional[str] = None
    number_watched: int
    total_movies: int