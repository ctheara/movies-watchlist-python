import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import DB_CONNECTION_STRING

Base = declarative_base()

if DB_CONNECTION_STRING:
    engine = create_engine(DB_CONNECTION_STRING, echo=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    engine = None
    SessionLocal = None

def get_db():
    if SessionLocal is None:
        raise RuntimeError(
            "Database is not configured. DB_CONNECTION_STRING is missing."
        )

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()