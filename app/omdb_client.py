import os
import requests
from app.config import OMDB_API_KEY
    
def search_movies(title: str, api_key: str = OMDB_API_KEY) -> list:
    url = "http://www.omdbapi.com/"
    params = {"apikey": api_key, "s": title, "page": 1}
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        return data.get('Search', [])
    else:
        print("Failed to search movies.")
        response.raise_for_status()
   
def fetch_movie_by_id(imdb_id: str, api_key: str = OMDB_API_KEY) -> dict:
    url = "http://www.omdbapi.com/"
    params = {"apikey": api_key, "i": imdb_id, "plot": 'full'}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch movie data.")
        response.raise_for_status()