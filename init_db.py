from app.database import Base, engine
from app.models import Movie

# Create all tables defined in your models
Base.metadata.create_all(bind=engine)

print("Database tables created or updated successfully!")
