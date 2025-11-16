import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from app.config import DB_CONNECTION_STRING

DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING")

engine = create_engine(DB_CONNECTION_STRING)

Base = declarative_base()