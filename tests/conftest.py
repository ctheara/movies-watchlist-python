# conftest.py - Pytest configuration and shared fixtures
# This file is loaded BEFORE test collection, so env vars are set early

import os

# Set environment variables before any app imports happen
os.environ["DB_CONNECTION_STRING"] = "sqlite:///:memory:"
os.environ["OMDB_API_KEY"] = "test_api_key"
