import logging
import requests
from typing import List, Dict, Any, Optional
from app.config import OMDB_API_KEY

logger = logging.getLogger(__name__)

OMDB_API_URL = "https://www.omdbapi.com/"
REQUEST_TIMEOUT = 10  # 10sec

def search_movies(title: str, page: int = 1) -> List[Dict[str, Any]]:
    params = {
        "apikey": OMDB_API_KEY,
        "s": title,
        "page": page
    }
    
    try:
        response = requests.get(OMDB_API_URL, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("Response") == "False":
            logger.warning(f"OMDb API error for search '{title}': {data.get('Error', 'Unknown error')}")
            return []
        
        results = data.get('Search', [])
        logger.debug(f"Search for '{title}' returned {len(results)} results")
        return results
        
    except requests.Timeout:
        logger.error(f"Timeout searching for movies with title '{title}'")
        raise
    except requests.RequestException as e:
        logger.error(f"Failed to search movies for '{title}': {e}")
        raise


def fetch_movie_by_id(imdb_id: str) -> Optional[Dict[str, Any]]:
    params = {
        "apikey": OMDB_API_KEY,
        "i": imdb_id,
        "plot": "full"
    }
    
    try:
        response = requests.get(OMDB_API_URL, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("Response") == "False":
            logger.warning(f"Movie not found for IMDb ID '{imdb_id}': {data.get('Error', 'Unknown error')}")
            return None
        
        logger.debug(f"Successfully fetched movie details for '{imdb_id}'")
        return data
        
    except requests.Timeout:
        logger.error(f"Timeout fetching movie with ID '{imdb_id}'")
        raise
    except requests.RequestException as e:
        logger.error(f"Failed to fetch movie data for '{imdb_id}': {e}")
        raise