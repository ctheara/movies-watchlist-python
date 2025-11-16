from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas
from app import omdb_client

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
def get_watchlist(db: Session = Depends(get_db)):
    movies = crud.get_all_movies(db)
    return movies

# add movie to watchlist, input movie data
# @app.post('/api/v1/movies')

# update watched status, input: imdb_id, watched(boolean), output: updated movie details
# @app.patch("/api/v1/movies/{imdb_id}/watched")

# delete movie, input: imdb_id, output: deleted movie details
# @app.delete("/api/v1/movies/{imdb_id}")

# get watched movies, output: list of watched movies
# @app.get('/api/v1/movies/watched', response_model=list[schemas.MovieResponse])