from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from app.analytics import compute_movie_stats
from app.database import get_db
from app import crud, schemas
from app import omdb_client
from typing import Optional
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Movie Watchlist API starting up...")
    yield
    logging.info("Movie Watchlist API shutting down...")

app = FastAPI(
    title="Movie Watchlist API",
    description="Personal movie watchlist with OMDb integration",
    version="1.0.0",
    lifespan=lifespan
)

# search movies, input: title, output: list of movies
@app.get("/api/v1/search/{title}")
def search_movies(title: str):
    try:
        results = omdb_client.search_movies(title)
        return results
    except Exception as e:
        logging.warning(f'Error searching movies: {e}')
        raise HTTPException(status_code=503, detail="Movie search service unavailable")

# fetch movies by id, input: imdb_id, output: movie details
@app.get("/api/v1/movies/{imdb_id}")
def get_movie_details(imdb_id: str):
    try:
        movie = omdb_client.fetch_movie_by_id(imdb_id)
        if not movie or movie.get("Response") == "False":
            raise HTTPException(status_code=404, detail="Movie not found")
        return movie
    except Exception as e:
        logging.warning(f'Error fetching movie details: {e}')
        raise HTTPException(status_code=503, detail="Movie details service unavailable")

# get movie watchlist, output: list of movies
@app.get("/api/v1/movies/", response_model=list[schemas.MovieResponse])
def get_watchlist(watched: Optional[bool] = None, db: Session = Depends(get_db)):
    if watched is None:
        return crud.get_movie_watchlist(db)
    return crud.get_movies_by_watched_status(db, watched)

# add movie to watchlist, input movie data
@app.post('/api/v1/movies', response_model=schemas.MovieResponse, status_code=201)
def add_movie_to_watchlist(req_body: schemas.MovieCreate, db: Session = Depends(get_db)):
    movie_data = omdb_client.fetch_movie_by_id(req_body.imdb_id)
    if not movie_data or movie_data.get("Response") == "False":
        raise HTTPException(status_code=404, detail="Movie not found")
    
    status, movie = crud.add_movie(db, movie_data)
    if status == "already_exists":
        raise HTTPException(status_code=400, detail="Movie is already in your watchlist")
    
    return movie

# update watched status, input: imdb_id, watched(boolean), output: updated movie details
@app.patch("/api/v1/movies/{imdb_id}/watched", response_model=schemas.MovieWatchedResponse)
def update_movie_status(
    imdb_id: str, 
    watched: bool,
    db: Session = Depends(get_db)
):
    updated_movie = crud.update_watched_status(db, imdb_id, watched)
    
    if not updated_movie:
        logging.warning(f"Attempt to update non-existent movie: {imdb_id}")
        raise HTTPException(status_code=404, detail="Movie not found")
    return updated_movie

# delete movie, input: imdb_id, output: deleted movie details
@app.delete("/api/v1/movies/{imdb_id}", response_model=schemas.MovieResponse)
def delete_movie(imdb_id: str, db: Session = Depends(get_db)):
    deleted_movie = crud.delete_movie(db, imdb_id)

    if not deleted_movie:
        logging.warning(f"Attempt to delete non-existent movie: {imdb_id}")
        raise HTTPException(status_code=404, detail="Movie not found")
    
    return deleted_movie

@app.get("/api/v1/analytics", response_model=schemas.AnalyticsResponse)
def get_analytics(db: Session = Depends(get_db)):
    return compute_movie_stats(db)