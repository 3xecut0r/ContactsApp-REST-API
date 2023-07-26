from typing import List
from datetime import date, timedelta

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy import and_

from src.database.models import Contact, User
from src.schemas import ContactModel


async def get_all_contacts(user: User, db: Session) -> List[Contact]:
    return db.query(Contact).filter(Contact.user_id == user.id).all()


async def get_contact(contact_id: int, user: User, db: Session) -> Contact:
    return db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()


async def create_contact(body: ContactModel, user: User, db: Session):
    contact = Contact(**body.dict(), user_id=user.id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def put_contact(contact_id: int, first_name: str, last_name: str, email: str, phone: str,
                      user: User, db: Session) -> Contact:
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
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if not contact:
        return None
    db.delete(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def search(first_name: str, last_name: str, email: str, user: User, db: Session):
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
    today = date.today()
    next_week = today + timedelta(days=7)
    return db.query(Contact).filter(
        and_(Contact.user_id == user.id, (Contact.birthday >= today) & (Contact.birthday <= next_week))
    ).all()

