from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Incoming POST request
class MovieCreate(BaseModel):
    imdb_id: str
    title: str
    year: str
    genre: Optional[str]
    rating: Optional[float] = None
    plot: Optional[str]
    poster_url: Optional[str]

# Outgoing response model
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