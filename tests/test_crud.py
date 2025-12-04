# For unit tests of crud.py. integration tests with a real SQLLite in-memory database
# create tables ffresh before each test and use SQLAlchemy Session for real queries.
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Movie
from app import crud

# SQLite in-memory DB
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(autouse=True)
def setup_tables():
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture
def db():
    session = TestSessionLocal()
    yield session
    session.close()

def sample_movie_data(
    imdb_id="tt1375666",
    title="Inception",
    year="2010",
    genre="Action",
    imdb_rating="8.8",
    plot="Test plot",
    poster="http://example.com/poster.jpg"
):
    return {
        "imdbID": imdb_id,
        "Title": title,
        "Year": year,
        "Genre": genre,
        "imdbRating": imdb_rating,
        "Plot": plot,
        "Poster": poster
    }

# Test adding a new movie
def test_add_movie_success(db):
    data = sample_movie_data()
    status, movie = crud.add_movie(db, data)

    assert status == "created"
    assert movie.title == data["Title"]
    assert movie.imdb_id == data["imdbID"]

# Test adding a duplicate movie
def test_add_movie_duplicate(db):
    data = sample_movie_data()
    crud.add_movie(db, data)

    status, movie = crud.add_movie(db, data)  # Add again

    assert status == "already_exists"

# Test with only required fields
def test_add_movie_minimal_fields(db):
    data = {
        "imdbID": "tt1234567",
        "Title": "Minimal Movie",
        "Year": "2020",
        "Genre": None,
        "imdbRating": None,
        "Plot": None,
        "Poster": None
    }
    status, movie = crud.add_movie(db, data)

    assert status == "created"
    assert movie.title == data["Title"]
    assert movie.genre is None
    assert movie.rating is None

# Test with missing required fields
def test_add_movie_missing_required_fields(db):
    data = {
        "imdbID": "tt1234567",
        # Missing Title
        "Year": "2020",
        "Genre": None,
        "imdbRating": None,
        "Plot": None,
        "Poster": None
    }
    with pytest.raises(KeyError):
        crud.add_movie(db, data)

# Test getting the watchlist (unwatched movies)
def test_get_movie_watchlist(db):
    movie1 = sample_movie_data(imdb_id="tt1111111", title="Movie 1")
    movie2 = sample_movie_data(imdb_id="tt2222222", title="Movie 2")
    crud.add_movie(db, movie1)
    crud.add_movie(db, movie2)

    crud.update_watched_status(db, movie1["imdbID"], True)

    watchlist = crud.get_movie_watchlist(db)
    assert len(watchlist) == 1
    assert all(not movie.watched for movie in watchlist)

# Test getting watched movies
def test_get_watched_movies(db):
    movie1 = sample_movie_data(imdb_id="tt1111111", title="Movie 1")
    movie2 = sample_movie_data(imdb_id="tt2222222", title="Movie 2")
    movie3 = sample_movie_data(imdb_id="tt3333333", title="Movie 3")
    crud.add_movie(db, movie1)
    crud.add_movie(db, movie2)
    crud.add_movie(db, movie3)

    crud.update_watched_status(db, movie1["imdbID"], True)
    crud.update_watched_status(db, movie3["imdbID"], True)

    watched_list = crud.get_movies_by_watched_status(db, True)
    assert len(watched_list) == 2

# Test getting all movies
def test_get_all_movies(db):
    movie1 = sample_movie_data(imdb_id="tt1111111", title="Movie 1")
    movie2 = sample_movie_data(imdb_id="tt2222222", title="Movie 2")
    movie3 = sample_movie_data(imdb_id="tt3333333", title="Movie 3")
    crud.add_movie(db, movie1)
    crud.add_movie(db, movie2)
    crud.add_movie(db, movie3)

    crud.update_watched_status(db, movie1["imdbID"], True)
    all_movies = crud.get_all_movies(db)
    assert len(all_movies) == 3

# Test updating watched status
def test_update_watched_status(db):
    data = sample_movie_data()
    crud.add_movie(db, data)

    updated_movie = crud.update_watched_status(db, data["imdbID"], True)
    assert updated_movie.watched is True

    updated_movie = crud.update_watched_status(db, data["imdbID"], False)
    assert updated_movie.watched is False


# Test update watched status on non-existent movie
def test_update_watched_status_non_existent(db):
    updated_movie = crud.update_watched_status(db, "tt0000000", True)
    assert updated_movie is None

# Test deleteting a movie
def test_deleting_movie(db):
    movie1 = sample_movie_data(imdb_id="tt1111111", title="Movie 1")
    movie2 = sample_movie_data(imdb_id="tt2222222", title="Movie 2")
    movie3 = sample_movie_data(imdb_id="tt3333333", title="Movie 3")
    crud.add_movie(db, movie1)
    crud.add_movie(db, movie2)
    crud.add_movie(db, movie3)

    crud.delete_movie(db, movie1["imdbID"])

    all_movies = crud.get_all_movies(db)
    assert len(all_movies) == 2

    movie = db.query(Movie).filter_by(imdb_id=movie1["imdbID"]).first()
    assert movie is None

# Test deleting a non-existent movie
def test_deleting_non_existent_movie(db):
    deleted_movie = crud.delete_movie(db, "tt0000000")
    assert deleted_movie is None

# Test getting total movies count
def test_get_total_movies(db):
    movie1 = sample_movie_data(imdb_id="tt1111111", title="Movie 1")
    movie2 = sample_movie_data(imdb_id="tt2222222", title="Movie 2")
    crud.add_movie(db, movie1)
    crud.add_movie(db, movie2)

    total_count = crud.get_total_movies(db)
    assert total_count == 2

# Test getting watched movies count
def test_get_watched_movies_count(db):
    movie1 = sample_movie_data(imdb_id="tt1111111", title="Movie 1")
    movie2 = sample_movie_data(imdb_id="tt2222222", title="Movie 2")
    movie3 = sample_movie_data(imdb_id="tt3333333", title="Movie 3")
    crud.add_movie(db, movie1)
    crud.add_movie(db, movie2)
    crud.add_movie(db, movie3)

    crud.update_watched_status(db, movie1["imdbID"], True)
    crud.update_watched_status(db, movie3["imdbID"], True)

    watched_count = crud.get_watched_movies_count(db)
    assert watched_count == 2




