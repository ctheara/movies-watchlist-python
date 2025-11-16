from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas
from app import omdb_client
from typing import Optional

app = FastAPI()

# search movies, input: title, output: list of movies
@app.get("/api/v1/search/{title}")
def search_movies(title: str):
    results = omdb_client.search_movies(title)
    return results

# fetch movies by id, input: imdb_id, output: movie details
@app.get("/api/v1/movies/{imdb_id}")
def fetch_movie(imdb_id: str):
    movie = omdb_client.fetch_movie_by_id(imdb_id)
    return movie

# get movie watchlist, output: list of movies
@app.get("/api/v1/movies/", response_model=list[schemas.MovieResponse])
def get_watchlist(watched: Optional[bool] = None, db: Session = Depends(get_db)):
    if watched is None:
        return crud.get_movie_watchlist(db)
    return crud.get_movies_by_watched_status(db, watched)

# add movie to watchlist, input movie data
# @app.post('/api/v1/movies')

# update watched status, input: imdb_id, watched(boolean), output: updated movie details
@app.patch("/api/v1/movies/{imdb_id}/watched", response_model=schemas.MovieWatchedResponse)
def update_movie_status(
    imdb_id: str, 
    watched: bool, 
    db: Session = Depends(get_db)
):
    updated_movie = crud.update_watched_status(db, imdb_id, watched)
    
    if not updated_movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return updated_movie

# delete movie, input: imdb_id, output: deleted movie details
@app.delete("/api/v1/movies/{imdb_id}", response_model=schemas.MovieResponse)
def delete_movie(imdb_id: str, db: Session = Depends(get_db)):
    deleted_movie = crud.delete_movie(db, imdb_id)

    if not deleted_movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    print(deleted_movie)
    return deleted_movie