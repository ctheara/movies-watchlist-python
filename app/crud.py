from sqlalchemy import Session
from app import models, schemas
    
def add_movie(db: Session, movie_data: schemas.MovieCreate):
    movie = models.Movie(**movie_data.model_dump())
    db.add(movie)
    db.commit()
    db.refresh(movie)
    return movie

def get_all_movies(db: Session):
    return db.query(models.Movie).all()

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
