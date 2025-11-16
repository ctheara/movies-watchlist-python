from dotenv import load_dotenv
import os

load_dotenv()

DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING")
OMDB_API_KEY = os.getenv("OMDB_API_KEY")