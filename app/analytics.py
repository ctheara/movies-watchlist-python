# app/analytics.py
from sqlalchemy.orm import Session
import pandas as pd
import logging
from typing import Dict, Optional
from app.schemas import AnalyticsResponse
from . import crud

logger = logging.getLogger(__name__)

def compute_movie_stats(db: Session) -> Dict[str, Optional[float | str | int]]:
    """
    Compute movie insights for analytics endpoint.
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with analytics data:
        - average_rating (float | None): Mean rating of all movies with ratings
        - most_frequent_genre (str | None): Most common genre across all movies
        - number_watched (int): Count of movies marked as watched
        - total_movies (int): Total number of movies in watchlist
    """
    # Fetch all movies from DB
    movies = crud.get_all_movies(db)
    
    # Handle empty database early
    if not movies:
        logger.debug("No movies found in database for analytics")
        return {
            "average_rating": None,
            "most_frequent_genre": None,
            "number_watched": 0,
            "total_movies": 0
        }

    # Convert to pandas DataFrame
    df = pd.DataFrame([{
        "title": m.title,
        "genre": m.genre,
        "rating": m.rating,
        "watched": m.watched
    } for m in movies])
    
    # Calculate average rating (excluding None/NaN values)
    ratings = df["rating"].dropna()
    average_rating = round(ratings.mean(), 2) if not ratings.empty else None
    
    # Calculate most frequent genre (excluding None/NaN values)
    genres = df["genre"].dropna()
    genre_mode = genres.mode()
    most_frequent_genre = genre_mode[0] if len(genre_mode) > 0 else None
    
    # Count watched movies (convert to int to ensure JSON serialization)
    number_watched = int(df["watched"].sum())
    
    # Total movies count
    total_movies = len(df)
    
    logger.debug(
        f"Analytics computed: {total_movies} total, {number_watched} watched, "
        f"avg rating {average_rating}, most frequent genre '{most_frequent_genre}'"
    )

    return {
        "average_rating": average_rating,
        "most_frequent_genre": most_frequent_genre,
        "number_watched": number_watched,
        "total_movies": total_movies
    }
