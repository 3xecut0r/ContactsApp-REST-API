from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.conf.config import settings


# Get the SQLAlchemy database URL from your settings
SQLALCHEMY_DATABASE_URL = settings.sqlalchemy_database_url

# Create an SQLAlchemy engine using the database URL
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a session factory using the engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for your declarative models
Base = declarative_base()


# Dependency to provide a database session to API routes
def get_db():
    """
    Dependency function to provide a database session to API routes.

    Yields:
        Session: SQLAlchemy database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
