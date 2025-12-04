# Unit tests for main.py
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime
from app.main import app

client = TestClient(app)

# Mock database dependency
def mock_get_db():
    db = MagicMock()
    try:
        yield db
    finally:
        pass


class TestSearchMovies:
    @patch('app.main.omdb_client.search_movies')
    def test_search_movies_success(self, mock_search):
        mock_search.return_value = [
            {"Title": "Inception", "Year": "2010", "imdbID": "tt1375666", "Type": "movie"}
        ]
        
        response = client.get("/api/v1/search/Inception")
        
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["Title"] == "Inception"
        mock_search.assert_called_once_with("Inception")

    @patch('app.main.omdb_client.search_movies')
    def test_search_movies_empty_results(self, mock_search):
        mock_search.return_value = []
        
        response = client.get("/api/v1/search/NonexistentMovie123")
        
        assert response.status_code == 200
        assert response.json() == []


class TestFetchMovie:
    @patch('app.main.omdb_client.fetch_movie_by_id')
    def test_fetch_movie_success(self, mock_fetch):
        mock_fetch.return_value = {
            "Title": "Inception",
            "Year": "2010",
            "imdbID": "tt1375666",
            "Genre": "Action, Sci-Fi",
            "imdbRating": "8.8"
        }
        
        response = client.get("/api/v1/movies/tt1375666")
        
        assert response.status_code == 200
        assert response.json()["Title"] == "Inception"
        mock_fetch.assert_called_once_with("tt1375666")


class TestGetWatchlist:
    @patch('app.main.get_db', mock_get_db)
    @patch('app.main.crud.get_movie_watchlist')
    def test_get_all_movies(self, mock_get_watchlist):
        mock_movie = MagicMock()
        mock_movie.imdb_id = "tt1375666"
        mock_movie.title = "Inception"
        mock_movie.year = "2010"
        mock_movie.genre = "Action, Sci-Fi"
        mock_movie.rating = 8.8
        mock_movie.plot = "A thief who steals corporate secrets"
        mock_movie.poster_url = "https://example.com/poster.jpg"
        mock_movie.watched = False
        mock_movie.date_added = datetime(2024, 1, 1)
        
        mock_get_watchlist.return_value = [mock_movie]
        
        response = client.get("/api/v1/movies/")
        
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["title"] == "Inception"

    @patch('app.main.get_db', mock_get_db)
    @patch('app.main.crud.get_movies_by_watched_status')
    def test_get_watched_movies(self, mock_get_by_status):
        mock_movie = MagicMock()
        mock_movie.imdb_id = "tt1375666"
        mock_movie.title = "Inception"
        mock_movie.year = "2010"
        mock_movie.genre = "Action, Sci-Fi"
        mock_movie.rating = 8.8
        mock_movie.plot = None
        mock_movie.poster_url = None
        mock_movie.watched = True
        mock_movie.date_added = datetime(2024, 1, 1)
        
        mock_get_by_status.return_value = [mock_movie]
        
        response = client.get("/api/v1/movies/?watched=true")
        
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["watched"] is True


class TestAddMovieToWatchlist:
    @patch('app.main.get_db', mock_get_db)
    @patch('app.main.crud.add_movie')
    @patch('app.main.omdb_client.fetch_movie_by_id')
    def test_add_movie_success(self, mock_fetch, mock_add):
        mock_fetch.return_value = {
            "Title": "Inception",
            "Year": "2010",
            "imdbID": "tt1375666",
            "Genre": "Action, Sci-Fi",
            "imdbRating": "8.8",
            "Response": "True"
        }
        
        mock_movie = MagicMock()
        mock_movie.imdb_id = "tt1375666"
        mock_movie.title = "Inception"
        mock_movie.year = "2010"
        mock_movie.genre = "Action, Sci-Fi"
        mock_movie.rating = 8.8
        mock_movie.plot = None
        mock_movie.poster_url = None
        mock_movie.watched = False
        mock_movie.date_added = datetime(2024, 1, 1)
        
        mock_add.return_value = ("created", mock_movie)
        
        response = client.post("/api/v1/movies", json={"imdb_id": "tt1375666"})
        
        assert response.status_code == 200
        assert response.json()["title"] == "Inception"

    @patch('app.main.get_db', mock_get_db)
    @patch('app.main.omdb_client.fetch_movie_by_id')
    def test_add_movie_not_found_in_omdb(self, mock_fetch):
        mock_fetch.return_value = {"Response": "False", "Error": "Movie not found!"}
        
        response = client.post("/api/v1/movies", json={"imdb_id": "tt0000000"})
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Movie not found"

    @patch('app.main.get_db', mock_get_db)
    @patch('app.main.crud.add_movie')
    @patch('app.main.omdb_client.fetch_movie_by_id')
    def test_add_movie_already_exists(self, mock_fetch, mock_add):
        mock_fetch.return_value = {
            "Title": "Inception",
            "Response": "True"
        }
        mock_add.return_value = ("already_exists", None)
        
        response = client.post("/api/v1/movies", json={"imdb_id": "tt1375666"})
        
        assert response.status_code == 400
        assert response.json()["detail"] == "Movie is already in your watchlist"


class TestUpdateMovieStatus:
    @patch('app.main.get_db', mock_get_db)
    @patch('app.main.crud.update_watched_status')
    def test_update_watched_status_success(self, mock_update):
        mock_movie = MagicMock()
        mock_movie.imdb_id = "tt1375666"
        mock_movie.title = "Inception"
        mock_movie.watched = True
        
        mock_update.return_value = mock_movie
        
        response = client.patch("/api/v1/movies/tt1375666/watched?watched=true")
        
        assert response.status_code == 200
        assert response.json()["watched"] is True
        assert response.json()["imdb_id"] == "tt1375666"

    @patch('app.main.get_db', mock_get_db)
    @patch('app.main.crud.update_watched_status')
    def test_update_watched_status_not_found(self, mock_update):
        mock_update.return_value = None
        
        response = client.patch("/api/v1/movies/tt0000000/watched?watched=true")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Movie not found"


class TestDeleteMovie:
    @patch('app.main.get_db', mock_get_db)
    @patch('app.main.crud.delete_movie')
    def test_delete_movie_success(self, mock_delete):
        mock_movie = MagicMock()
        mock_movie.imdb_id = "tt1375666"
        mock_movie.title = "Inception"
        mock_movie.year = "2010"
        mock_movie.genre = "Action, Sci-Fi"
        mock_movie.rating = 8.8
        mock_movie.plot = None
        mock_movie.poster_url = None
        mock_movie.watched = False
        mock_movie.date_added = datetime(2024, 1, 1)
        
        mock_delete.return_value = mock_movie
        
        response = client.delete("/api/v1/movies/tt1375666")
        
        assert response.status_code == 200
        assert response.json()["title"] == "Inception"
        mock_delete.assert_called_once()

    @patch('app.main.get_db', mock_get_db)
    @patch('app.main.crud.delete_movie')
    def test_delete_movie_not_found(self, mock_delete):
        mock_delete.return_value = None
        
        response = client.delete("/api/v1/movies/tt0000000")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Movie not found"


class TestGetAnalytics:
    @patch('app.main.get_db', mock_get_db)
    @patch('app.main.compute_movie_stats')
    def test_get_analytics_success(self, mock_stats):
        mock_stats.return_value = {
            "average_rating": 7.5,
            "most_frequent_genre": "Drama",
            "number_watched": 5,
            "total_movies": 10
        }
        
        response = client.get("/api/v1/analytics")
        
        assert response.status_code == 200
        assert response.json()["average_rating"] == 7.5
        assert response.json()["most_frequent_genre"] == "Drama"
        assert response.json()["number_watched"] == 5
        assert response.json()["total_movies"] == 10

    @patch('app.main.get_db', mock_get_db)
    @patch('app.main.compute_movie_stats')
    def test_get_analytics_empty_database(self, mock_stats):
        mock_stats.return_value = {
            "average_rating": None,
            "most_frequent_genre": None,
            "number_watched": 0,
            "total_movies": 0
        }
        
        response = client.get("/api/v1/analytics")
        
        assert response.status_code == 200
        assert response.json()["average_rating"] is None
        assert response.json()["total_movies"] == 0