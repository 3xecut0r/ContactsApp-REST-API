from typing import List
from datetime import date, timedelta

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy import and_

from src.database.models import Contact, User
from src.schemas import ContactModel


async def get_all_contacts(user: User, db: Session) -> List[Contact]:
    """
    Get all contacts belonging to a user.

    Args:
        user (User): The user whose contacts are to be retrieved.
        db (Session): The database session.

    Returns:
        List[Contact]: A list of contacts belonging to the user.
    """
    return db.query(Contact).filter(Contact.user_id == user.id).all()


async def get_contact(contact_id: int, user: User, db: Session) -> Contact:
    """
    Get a specific contact belonging to a user.

    Args:
        contact_id (int): The ID of the contact to retrieve.
        user (User): The user who owns the contact.
        db (Session): The database session.

    Returns:
        Optional[Contact]: The requested contact or None if not found.
    """
    return db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()


async def create_contact(body: ContactModel, user: User, db: Session):
    """
    Create a new contact for a user.

    Args:
        body (ContactModel): The data for the new contact.
        user (User): The user who owns the contact.
        db (Session): The database session.

    Returns:
        Contact: The created contact.
    """
    contact = Contact(**body.model_dump(), user_id=user.id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def put_contact(contact_id: int, first_name: str, last_name: str, email: str, phone: str,
                      user: User, db: Session) -> Contact:
    """
    Update a contact's information.

    Args:
        contact_id (int): The ID of the contact to update.
        first_name (str): New first name (if provided).
        last_name (str): New last name (if provided).
        email (str): New email address (if provided).
        phone (str): New phone number (if provided).
        user (User): The user who owns the contact.
        db (Session): The database session.

    Returns:
        Optional[Contact]: The updated contact or None if not found.
    """
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if contact is None:
        return None
    if first_name is not None:
        contact.first_name = first_name
    if last_name is not None:
        contact.last_name = last_name
    if email is not None:
        contact.email = email
    if phone is not None:
        contact.phone = phone
    db.commit()
    db.refresh(contact)
    return contact


async def del_contact(contact_id: int, user: User, db: Session):
    """
    Delete a contact.

    Args:
        contact_id (int): The ID of the contact to delete.
        user (User): The user who owns the contact.
        db (Session): The database session.

    Returns:
        Optional[Contact]: The deleted contact or None if not found.
    """
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if not contact:
        return None
    db.delete(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def search(first_name: str, last_name: str, email: str, user: User, db: Session):
    """
    Search contacts based on given criteria.

    Args:
        first_name (str): First name to search for (partial match).
        last_name (str): Last name to search for (partial match).
        email (str): Email to search for (partial match).
        user (User): The user whose contacts are to be searched.
        db (Session): The database session.

    Returns:
        List[Contact]: List of matching contacts.
    """
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    contacts = db.query(Contact).filter(
        (Contact.first_name.ilike(f'%{first_name}%')) |
        (Contact.last_name.ilike(f'%{last_name}%')) |
        (Contact.email.ilike(f'%{email}%'))
    ).all()
    if not contacts:
        return None
    return contacts


async def birthdays(user: User, db: Session):
    """
    Get contacts with upcoming birthdays within the next week.

    Args:
        user (User): The user whose contacts are to be considered.
        db (Session): The database session.

    Returns:
        List[Contact]: List of contacts with upcoming birthdays.
    """
    today = date.today()
    next_week = today + timedelta(days=7)
    return db.query(Contact).filter(
        and_(Contact.user_id == user.id, (Contact.birthday >= today) & (Contact.birthday <= next_week))
    ).all()

