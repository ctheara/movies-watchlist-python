from pydantic import BaseModel
from typing import Optional

class MovieCreate(BaseModel):
    imdb_id: str
    title: str
    year: str
    genre: Optional[str]
    rating: Optional[str]
    plot: Optional[str]
    poster_url: Optional[str]