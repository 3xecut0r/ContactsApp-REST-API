from sqlalchemy import Column, Integer, String, DateTime, func, Boolean
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql.schema import ForeignKey

from src.database.db import engine

Base = declarative_base()


class Contact(Base):
    """
    SQLAlchemy model representing a contact.

    Attributes:
        id (int): Primary key of the contact.
        first_name (str): First name of the contact.
        last_name (str): Last name of the contact.
        email (str): Email address of the contact (unique).
        phone (str): Phone number of the contact (unique).
        birthday (datetime): Birthday of the contact.
        created_at (datetime): Creation timestamp of the contact.
        updated_at (datetime): Last update timestamp of the contact.
        user_id (int): Foreign key referencing the user this contact belongs to.

    Relationships:
        user (User): Relationship to the User model.
    """
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, unique=True, nullable=False)
    birthday = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    user_id = Column(ForeignKey('users.id', ondelete='CASCADE'), default=None)
    user = relationship('User', backref='contacts')


class User(Base):
    """
    SQLAlchemy model representing a user.

    Attributes:
        id (int): Primary key of the user.
        username (str): Username of the user (up to 50 characters).
        email (str): Email address of the user (unique, up to 250 characters).
        password (str): Hashed password of the user.
        created_at (datetime): Creation timestamp of the user.
        avatar (str, optional): URL to the user's avatar image.
        refresh_token (str, optional): Refresh token for authentication.
        confirmed (bool): Whether the user's email is confirmed.

    Relationships:
        contacts (List[Contact]): List of contacts associated with the user.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    email = Column(String(250), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)


# Create all defined tables in the database
Base.metadata.create_all(bind=engine)
