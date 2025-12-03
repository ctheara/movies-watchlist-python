# Movie Watchlist App

This small service helps you keep a personal watchlist of movies. It uses the OMDb API to fetch movie metadata (title, genres, ratings, plot, etc.), stores selected movies in a PostgreSQL database, and exposes REST APIs to manage and query your watchlist.

## Features

- Search movies by title (OMDb)
- Retrieve full movie details by IMDb ID
- Add movies to a persistent watchlist
- Mark movies as watched or unwatched
- Delete movies from the watchlist

## Tech stack

- Python 3.8+
- FastAPI
- PostgreSQL
- SQLAlchemy
- Requests
- python-dotenv
- Pandas

## Setup instructions

1. Create and activate a virtual environment (recommended):

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```
python -m pip install -r requirements.txt
```

3. Create a `.env` file in the project root with at least these variables:

```
DB_CONNECTION_STRING=postgresql://user:password@localhost:5432/movies_db
OMDB_API_KEY=your_omdb_api_key_here
```

4. Initialize the database (creates tables defined in `app/models.py`):

```
python init_db.py
```

5. Run the API locally:

```
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Interactive docs: `http://127.0.0.1:8000/docs`

## Example requests & responses

1. Search movies

Request:

```
GET /api/v1/search/Inception
```

Example response (OMDb `Search` simplified):

```json
[
  {
    "Title": "Inception",
    "Year": "2010",
    "imdbID": "tt1375666",
    "Type": "movie",
    "Poster": "https://..."
  },
  {
    ...
  }
]
```

2. Get movie details

Request:

```
GET /api/v1/movies/tt1375666
```

Example response (OMDb full movie payload, trimmed):

```json
{
  "Title": "Inception",
  "Year": "2010",
  "Rated": "PG-13",
  "Released": "16 Jul 2010",
  "Runtime": "148 min",
  "Genre": "Action, Adventure, Sci-Fi",
  "Director": "Christopher Nolan",
  "Actors": "Leonardo DiCaprio, Joseph Gordon-Levitt, Ellen Page",
  "imdbRating": "8.8",
  "imdbID": "tt1375666"
}
```

3. Add movie to watchlist

Request:

```
POST /api/v1/movies
Content-Type: application/json

{ "imdb_id": "tt1375666" }
```

Example response (stored watchlist item):

```json
{
  "id": 1,
  "title": "Inception",
  "imdb_id": "tt1375666",
  "genre": "Action, Adventure, Sci-Fi",
  "rating": 8.8,
  "watched": false
}
```

4. Update watched status

Request:

```
PATCH /api/v1/movies/tt1375666/watched?watched=true
```

Example response:

```json
{
  "imdb_id": "tt1375666",
  "watched": true
}
```

5. Get watchlist

Request:

```
GET /api/v1/movies/
```

Example response:

```json
[
  {
    "id": 1,
    "title": "Inception",
    "imdb_id": "tt1375666",
    "genre": "Action, Adventure, Sci-Fi",
    "rating": 8.8,
    "watched": true
  }
]
```

## Analytics explanation

There is a small analytics helper implemented at `app/analytics.py` which computes simple insights from the stored watchlist. The function `compute_movie_stats(db: Session)`:

- Loads all movies from the database via the CRUD layer.
- Converts movie records into a pandas `DataFrame`.
- Returns a dictionary with these fields:
  - `average_rating` (float|null): average of the `rating` column, rounded to 2 decimals. Returns `null` if there are no ratings.
  - `most_frequent_genre` (string|null): the most common genre among stored movies (uses pandas `mode`).
  - `number_watched` (int): count of movies marked as watched.
  - `total_movies` (int): total number of movies in the watchlist.

Example analytics response:

```json
{
  "average_rating": 7.95,
  "most_frequent_genre": "Drama",
  "number_watched": 12,
  "total_movies": 20
}
```

Note: `app/analytics.py` currently prints the DataFrame for debugging and expects the CRUD helper `get_all_movies(db)` to return ORM model instances with attributes `title`, `genre`, `rating`, and `watched`.

## Development notes

- Config values are loaded from environment variables using `python-dotenv` (`app/config.py`).
- Database initialization is done by `init_db.py` (creates tables via SQLAlchemy metadata).
- OMDb client is implemented in `app/omdb_client.py` and expects `OMDB_API_KEY` to be set.
