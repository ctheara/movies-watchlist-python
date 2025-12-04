# Unit tests for analytics.py
from unittest.mock import MagicMock, patch
from app.analytics import compute_movie_stats


class TestComputeMovieStats:
    
    def test_empty_database(self):
        """Test analytics with no movies in database"""
        mock_db = MagicMock()
        
        with patch('app.analytics.crud.get_all_movies') as mock_get_all:
            mock_get_all.return_value = []
            
            result = compute_movie_stats(mock_db)
            
            assert result["average_rating"] is None
            assert result["most_frequent_genre"] is None
            assert result["number_watched"] == 0
            assert result["total_movies"] == 0
    
    def test_single_movie_watched(self):
        """Test analytics with single watched movie"""
        mock_db = MagicMock()
        mock_movie = MagicMock()
        mock_movie.title = "Inception"
        mock_movie.genre = "Sci-Fi"
        mock_movie.rating = 8.8
        mock_movie.watched = True
        
        with patch('app.analytics.crud.get_all_movies') as mock_get_all:
            mock_get_all.return_value = [mock_movie]
            
            result = compute_movie_stats(mock_db)
            
            assert result["average_rating"] == 8.8
            assert result["most_frequent_genre"] == "Sci-Fi"
            assert result["number_watched"] == 1
            assert result["total_movies"] == 1
    
    def test_single_movie_unwatched(self):
        """Test analytics with single unwatched movie"""
        mock_db = MagicMock()
        mock_movie = MagicMock()
        mock_movie.title = "The Matrix"
        mock_movie.genre = "Action"
        mock_movie.rating = 8.7
        mock_movie.watched = False
        
        with patch('app.analytics.crud.get_all_movies') as mock_get_all:
            mock_get_all.return_value = [mock_movie]
            
            result = compute_movie_stats(mock_db)
            
            assert result["average_rating"] == 8.7
            assert result["most_frequent_genre"] == "Action"
            assert result["number_watched"] == 0
            assert result["total_movies"] == 1
    
    def test_multiple_movies_mixed_watched_status(self):
        """Test analytics with multiple movies, some watched and some not"""
        mock_db = MagicMock()
        
        movie1 = MagicMock()
        movie1.title = "Inception"
        movie1.genre = "Sci-Fi"
        movie1.rating = 8.8
        movie1.watched = True
        
        movie2 = MagicMock()
        movie2.title = "The Matrix"
        movie2.genre = "Sci-Fi"
        movie2.rating = 8.7
        movie2.watched = True
        
        movie3 = MagicMock()
        movie3.title = "Interstellar"
        movie3.genre = "Drama"
        movie3.rating = 8.6
        movie3.watched = False
        
        with patch('app.analytics.crud.get_all_movies') as mock_get_all:
            mock_get_all.return_value = [movie1, movie2, movie3]
            
            result = compute_movie_stats(mock_db)
            
            assert result["average_rating"] == 8.7  # (8.8 + 8.7 + 8.6) / 3 = 8.7
            assert result["most_frequent_genre"] == "Sci-Fi"  # 2 Sci-Fi vs 1 Drama
            assert result["number_watched"] == 2
            assert result["total_movies"] == 3
    
    def test_movies_with_none_ratings(self):
        """Test analytics when some movies have None ratings"""
        mock_db = MagicMock()
        
        movie1 = MagicMock()
        movie1.title = "Movie A"
        movie1.genre = "Drama"
        movie1.rating = 7.5
        movie1.watched = True
        
        movie2 = MagicMock()
        movie2.title = "Movie B"
        movie2.genre = "Comedy"
        movie2.rating = None
        movie2.watched = False
        
        movie3 = MagicMock()
        movie3.title = "Movie C"
        movie3.genre = "Drama"
        movie3.rating = 8.5
        movie3.watched = True
        
        with patch('app.analytics.crud.get_all_movies') as mock_get_all:
            mock_get_all.return_value = [movie1, movie2, movie3]
            
            result = compute_movie_stats(mock_db)
            
            # Average should handle None values (pandas will ignore them)
            assert result["average_rating"] == 8.0  # (7.5 + 8.5) / 2 = 8.0
            assert result["most_frequent_genre"] == "Drama"
            assert result["number_watched"] == 2
            assert result["total_movies"] == 3
    
    def test_all_movies_same_genre(self):
        """Test analytics when all movies have the same genre"""
        mock_db = MagicMock()
        
        movies = []
        for i in range(5):
            movie = MagicMock()
            movie.title = f"Action Movie {i+1}"
            movie.genre = "Action"
            movie.rating = 7.0 + i * 0.2
            movie.watched = i % 2 == 0  # Alternate watched status
            movies.append(movie)
        
        with patch('app.analytics.crud.get_all_movies') as mock_get_all:
            mock_get_all.return_value = movies
            
            result = compute_movie_stats(mock_db)
            
            assert result["most_frequent_genre"] == "Action"
            assert result["number_watched"] == 3  # movies 0, 2, 4
            assert result["total_movies"] == 5
            # Average: (7.0 + 7.2 + 7.4 + 7.6 + 7.8) / 5 = 7.4
            assert result["average_rating"] == 7.4
    
    def test_genres_with_equal_frequency(self):
        """Test analytics when multiple genres have the same frequency (mode returns first)"""
        mock_db = MagicMock()
        
        movie1 = MagicMock()
        movie1.title = "Drama 1"
        movie1.genre = "Drama"
        movie1.rating = 8.0
        movie1.watched = True
        
        movie2 = MagicMock()
        movie2.title = "Action 1"
        movie2.genre = "Action"
        movie2.rating = 7.5
        movie2.watched = False
        
        with patch('app.analytics.crud.get_all_movies') as mock_get_all:
            mock_get_all.return_value = [movie1, movie2]
            
            result = compute_movie_stats(mock_db)
            
            # When there's a tie, pandas mode() returns the first encountered
            assert result["most_frequent_genre"] in ["Drama", "Action"]
            assert result["number_watched"] == 1
            assert result["total_movies"] == 2
            assert result["average_rating"] == 7.75  # (8.0 + 7.5) / 2
    
    def test_all_movies_unwatched(self):
        """Test analytics when no movies have been watched"""
        mock_db = MagicMock()
        
        movie1 = MagicMock()
        movie1.title = "Movie A"
        movie1.genre = "Horror"
        movie1.rating = 6.5
        movie1.watched = False
        
        movie2 = MagicMock()
        movie2.title = "Movie B"
        movie2.genre = "Thriller"
        movie2.rating = 7.0
        movie2.watched = False
        
        with patch('app.analytics.crud.get_all_movies') as mock_get_all:
            mock_get_all.return_value = [movie1, movie2]
            
            result = compute_movie_stats(mock_db)
            
            assert result["number_watched"] == 0
            assert result["total_movies"] == 2
            assert result["average_rating"] == 6.75
    
    def test_all_movies_watched(self):
        """Test analytics when all movies have been watched"""
        mock_db = MagicMock()
        
        movie1 = MagicMock()
        movie1.title = "Movie A"
        movie1.genre = "Comedy"
        movie1.rating = 7.0
        movie1.watched = True
        
        movie2 = MagicMock()
        movie2.title = "Movie B"
        movie2.genre = "Comedy"
        movie2.rating = 8.0
        movie2.watched = True
        
        movie3 = MagicMock()
        movie3.title = "Movie C"
        movie3.genre = "Comedy"
        movie3.rating = 9.0
        movie3.watched = True
        
        with patch('app.analytics.crud.get_all_movies') as mock_get_all:
            mock_get_all.return_value = [movie1, movie2, movie3]
            
            result = compute_movie_stats(mock_db)
            
            assert result["number_watched"] == 3
            assert result["total_movies"] == 3
            assert result["average_rating"] == 8.0
            assert result["most_frequent_genre"] == "Comedy"
    
    def test_rounding_average_rating(self):
        """Test that average rating is properly rounded to 2 decimals"""
        mock_db = MagicMock()
        
        movie1 = MagicMock()
        movie1.title = "Movie A"
        movie1.genre = "Drama"
        movie1.rating = 7.777
        movie1.watched = False
        
        movie2 = MagicMock()
        movie2.title = "Movie B"
        movie2.genre = "Drama"
        movie2.rating = 8.888
        movie2.watched = True
        
        with patch('app.analytics.crud.get_all_movies') as mock_get_all:
            mock_get_all.return_value = [movie1, movie2]
            
            result = compute_movie_stats(mock_db)
            
            # (7.777 + 8.888) / 2 = 8.3325, rounded to 8.33
            assert result["average_rating"] == 8.33
            assert result["total_movies"] == 2
