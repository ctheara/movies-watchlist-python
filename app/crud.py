from sqlalchemy.orm import Session
from typing import Tuple, List, Optional
from app import models, schemas

def add_movie(db: Session, movie_data: dict) -> Tuple[str, Optional[models.Movie]]:
    existing_movie = db.query(models.Movie).filter_by(imdb_id=movie_data["imdbID"]).first()
    if existing_movie:
        return "already_exists", existing_movie
    
    movie_dict = {
        "imdb_id": movie_data["imdbID"],
        "title": movie_data["Title"],
        "year": movie_data["Year"],
        "genre": movie_data.get("Genre"),
        "rating": float(movie_data["imdbRating"]) if movie_data.get("imdbRating") not in [None, "N/A"] else None,
        "plot": movie_data.get("Plot"),
        "poster_url": movie_data.get("Poster")
    }

    movie = models.Movie(**movie_dict)
    db.add(movie)
    db.commit()
    db.refresh(movie)
    return "created", movie

def get_movie_watchlist(db: Session) -> List[models.Movie]:
    return db.query(models.Movie).filter(models.Movie.watched.is_(False)).all()

def get_all_movies(db: Session) -> List[models.Movie]:
    return db.query(models.Movie).all()

def get_movies_by_watched_status(db: Session, watched: bool) -> List[models.Movie]:
    return db.query(models.Movie).filter(models.Movie.watched.is_(watched)).all()

def update_watched_status(db: Session, imdb_id: str, watched: bool) -> Optional[models.Movie]:
    movie = db.query(models.Movie).filter_by(imdb_id=imdb_id).first()
    if movie:
        movie.watched = watched
        db.commit()
        db.refresh(movie)
        return movie
    return None

def delete_movie(db: Session, imdb_id: str) -> Optional[models.Movie]:
    movie = db.query(models.Movie).filter_by(imdb_id=imdb_id).first()
    if movie:
        db.delete(movie)
        db.commit()
        return movie
    return None

def get_total_movies(db: Session) -> int:
    return db.query(models.Movie).count()

def get_watched_movies_count(db: Session) -> int:
    return db.query(models.Movie).filter(models.Movie.watched.is_(True)).count()