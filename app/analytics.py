# app/analytics.py
from sqlalchemy.orm import Session
import pandas as pd
from app.schemas import AnalyticsResponse
from . import crud

def compute_movie_stats(db: Session) -> AnalyticsResponse:
    """
    Compute movie insights for analytics endpoint.
    
    Returns a dictionary with:
    - average_rating
    - most_frequent_genre
    - number_watched
    - total_movies
    """
    # Fetch all movies from DB
    movies = crud.get_all_movies(db)

    # Convert to pandas DataFrame
    df = pd.DataFrame([{
        "title": m.title,
        "genre": m.genre,
        "rating": m.rating,
        "watched": m.watched
    } for m in movies])
    print(df)

    # Handle empty DB
    if df.empty:
        return {
            "average_rating": None,
            "most_frequent_genre": None,
            "number_watched": 0,
            "total_movies": 0
        }

    average_rating = round(df["rating"].mean(), 2) if "rating" in df else None
    most_frequent_genre = df["genre"].mode()[0] if "genre" in df else None
    number_watched = df["watched"].sum() if "watched" in df else 0
    total_movies = len(df)

    return {
        "average_rating": average_rating,
        "most_frequent_genre": most_frequent_genre,
        "number_watched": number_watched,
        "total_movies": total_movies
    }
