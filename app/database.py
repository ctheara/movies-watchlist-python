import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()

DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING")

engine = create_engine(DB_CONNECTION_STRING)

Base = declarative_base()