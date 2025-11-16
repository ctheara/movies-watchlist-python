from fastapi import FastAPI
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

# update watched status, input: imdb_id, watched(boolean), output: updated movie details

# delete movie, input: imdb_id, output: deleted movie details

# get watched movies, output: list of watched movies