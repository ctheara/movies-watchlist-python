import pytest
from unittest.mock import patch, Mock, ANY
from app.omdb_client import search_movies, fetch_movie_by_id
from requests.exceptions import HTTPError

MOCK_SEARCH_SUCCESS = {
    "Search": [
        {"Title": "Inception", "Year": "2010", "imdbID": "tt1375666", "Type": "movie"},
        {"Title": "The Inception", "Year": "2020", "imdbID": "tt1375667", "Type": "movie"}
    ],
    "totalResults": "2",
    "Response": "True"
}

# Test searching for movies by title
@patch('app.omdb_client.requests.get')
def test_search_movies_success(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_SEARCH_SUCCESS
    mock_get.return_value = mock_response

    title_to_search = "Inception"
    results = search_movies(title_to_search)

    assert results == MOCK_SEARCH_SUCCESS["Search"]
    expected_url = "http://www.omdbapi.com/"
    expected_params = {
        "apikey": ANY,
        "s": title_to_search,
        "page": 1
    }
    mock_get.assert_called_once_with(expected_url, params=expected_params)

@patch("app.omdb_client.requests.get")
def test_search_movies_success(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "Search": [{"Title": "Inception", "Year": "2010", "imdbID": "tt1375666"}]
    }

    results = search_movies("Inception")
    assert len(results) == 1
    assert results[0]["Title"] == "Inception"

# Test searching for movies by not status 200
@patch("app.omdb_client.requests.get")
def test_search_movies_raises_http_error(mock_get):
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = HTTPError("500 Server Error: Internal Server Error")
    mock_get.return_value = mock_response

    title_to_search = "Inception"
    with pytest.raises(HTTPError):
        search_movies(title_to_search)

# Test searching for movies with no results
@patch("app.omdb_client.requests.get")
def test_search_movies_no_results(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {}
    results = search_movies("NonexistentMovie")
    assert results == []

# Test searching for movies with empty title
@patch("app.omdb_client.requests.get")
def test_search_movies_empty_title(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"Response": "False", "Error": "Incorrect IMDb ID."}
    
    results = search_movies("")
    assert results == []
    
    mock_get.assert_called_once_with(
        'http://www.omdbapi.com/',
        params={'apikey': ANY, 's': '', 'page': 1}
    )

# Test searching for movies with special characters
@patch("app.omdb_client.requests.get")
def test_search_movies_special_characters(mock_get):
    expected_data = [{"Title": "A vs B: The Movie", "imdbID": "tt1000001"}]
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"Search": expected_data, "Response": "True"}
    
    title_with_chars = "A vs B: The Movie & More"
    results = search_movies(title_with_chars)
    
    assert results == expected_data
    mock_get.assert_called_once_with(
        'http://www.omdbapi.com/',
        params={'apikey': ANY, 's': title_with_chars, 'page': 1}
    )

# Verify that searching movies returns expected fields
@patch('app.omdb_client.requests.get')
def test_search_movies_returns_expected_fields(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = MOCK_SEARCH_SUCCESS
    
    results = search_movies("Inception")
    
    assert len(results) > 0
    for movie in results:
        assert isinstance(movie, dict)
        assert "Title" in movie
        assert "imdbID" in movie
        assert "Year" in movie
        assert "Type" in movie

# Test fetching movie details by IMDb ID
@patch("app.omdb_client.requests.get")
def test_fetch_movie_success(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "Title": "Inception", "Year": "2010", "imdbID": "tt1375666", "Plot": "A movie", "imdbRating": "8.8"
    }
    movie = fetch_movie_by_id("tt1375666")
    assert movie["Title"] == "Inception"

# Test fetching movie details by not status 200
@patch("app.omdb_client.requests.get")
def test_fetch_movie_raises_http_error_on_status(mock_get):
    """
    Tests that fetch_movie_by_id raises a requests.exceptions.HTTPError 
    when the API returns a non-200 status code (e.g., 403 Forbidden).
    """
    mock_response = Mock()
    mock_response.status_code = 403
    mock_response.raise_for_status.side_effect = HTTPError("403 Client Error: Forbidden")
    mock_get.return_value = mock_response

    with pytest.raises(HTTPError):
        fetch_movie_by_id("tt1375666")
    mock_get.assert_called_once_with(
        'http://www.omdbapi.com/',
        params={'apikey': ANY, 'i': 'tt1375666', 'plot': 'full'}
    )

# Test invalid IMDb ID returns error
@patch("app.omdb_client.requests.get")
def test_fetch_movie_not_found(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"Response": "False", "Error": "Movie not found!"}
    movie = fetch_movie_by_id("invalidid")
    assert movie["Response"] == "False"

# Verify that fetching movie details returns expected fields
@patch("app.omdb_client.requests.get")
def test_fetch_movie_returns_expected_fields(mock_get):
    MOCK_MOVIE_DETAILS = {
        "Title": "Inception", "Year": "2010", "Rated": "PG-13", "Released": "16 Jul 2010",
        "Runtime": "148 min", "Genre": "Action, Adventure, Sci-Fi", "Plot": "A thief who steals corporate secrets...",
        "imdbRating": "8.8", "imdbID": "tt1375666", "Response": "True"
    }
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = MOCK_MOVIE_DETAILS
    
    movie = fetch_movie_by_id("tt1375666")
    
    assert isinstance(movie, dict)
    assert movie["Response"] == "True"
    assert "Plot" in movie
    assert "imdbRating" in movie
    assert movie["imdbID"] == "tt1375666"

# Test fetching movie details with empty IMDb ID
@patch("app.omdb_client.requests.get")
def test_fetch_movie_empty_id(mock_get):
    MOCK_ERROR_RESPONSE = {"Response": "False", "Error": "Incorrect IMDb ID."}
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = MOCK_ERROR_RESPONSE
    
    movie = fetch_movie_by_id("")
    
    assert movie == MOCK_ERROR_RESPONSE
    mock_get.assert_called_once_with(
        'http://www.omdbapi.com/',
        params={'apikey': ANY, 'i': '', 'plot': 'full'}
    )

# Test fetching movie details but imdbRating is "N/A"
@patch("app.omdb_client.requests.get")
def test_fetch_movie_rating_na(mock_get):
    MOCK_NA_RATING = {
        "Title": "Unrated Movie", "Year": "2025", 
        "imdbRating": "N/A", "imdbID": "tt2000000", "Response": "True"
    }
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = MOCK_NA_RATING
    
    movie = fetch_movie_by_id("tt2000000")
    
    assert movie["imdbRating"] == "N/A"
    assert movie["Response"] == "True"