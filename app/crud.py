from sqlalchemy.orm import Session
from app import models, schemas
    
def add_movie(db: Session, movie_data: schemas.MovieCreate):
    existing_movie = db.query(models.Movie).filter_by(imdb_id=movie_data["imdbID"]).first()
    if existing_movie:
        return "already_exists", existing_movie
    
    movie_dict = {
        "imdb_id": movie_data["imdbID"],
        "title": movie_data["Title"],
        "year": movie_data["Year"],
        "genre": movie_data["Genre"],
        "rating": float(movie_data["imdbRating"]) if movie_data.get("imdbRating") not in [None, "N/A"] else None,
        "plot": movie_data.get("Plot"),
        "poster_url": movie_data.get("Poster")
    }

    movie = models.Movie(**movie_dict)
    db.add(movie)
    db.commit()
    db.refresh(movie)
    return "created", movie

def get_movie_watchlist(db: Session):
    return db.query(models.Movie).filter(models.Movie.watched == False).all()

def get_all_movies(db: Session):
    return db.query(models.Movie).all()

def get_movies_by_watched_status(db: Session, watched: bool):
    return db.query(models.Movie).filter(models.Movie.watched == watched).all()

def update_watched_status(db: Session, imdb_id: str, watched: bool):
    movie = db.query(models.Movie).filter(models.Movie.imdb_id == imdb_id).first()
    if movie:
        movie.watched = watched
        db.commit()
        db.refresh(movie)
        return movie

def delete_movie(db: Session, imdb_id: str):
    movie = db.query(models.Movie).filter(models.Movie.imdb_id == imdb_id).first()
    if movie:
        db.delete(movie)
        db.commit()
        return movie

def get_total_movies(db: Session):
    return db.query(models.Movie).count()

def get_watched_movies_count(db: Session):
    return db.query(models.Movie).filter(models.Movie.watched == True).count()