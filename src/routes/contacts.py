from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session
import redis
from redis_lru import RedisLRU
import json

from src.database.db import get_db
from src.database.models import User
from src.schemas import ContactModel, ContactResponse
from src.repository import contacts as repository_contacts
from src.services.auth import auth_service


router = APIRouter(prefix='/contacts', tags=["contacts"])
r = redis.Redis(host='localhost', port=6379, db=0)
client = redis.StrictRedis()
cache = RedisLRU(client)


@router.post("/create", response_model=ContactResponse)
async def create_contact(contact: ContactModel,
                         current_user: User = Depends(auth_service.get_current_user),
                         db: Session = Depends(get_db)):
    """
    Create a new contact.

    Args:
        contact (ContactModel): Contact data from the request.
        current_user (User): The current user.
        db (Session): The database session.

    Returns:
        ContactResponse: The created contact.
    """
    return await repository_contacts.create_contact(contact, current_user, db)


@cache
@router.get("/all", description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_all(limit: int = 10, offset: int = 0, db: Session = Depends(get_db),
                  current_user: User = Depends(auth_service.get_current_user)):
    """
    Get a list of all contacts.

    Args:
        limit (int, optional): Maximum number of contacts to return. Defaults to 10.
        offset (int, optional): Offset for pagination. Defaults to 0.
        db (Session): The database session.
        current_user (User): The current user.

    Returns:
        List[Contact]: List of contacts.
    """
    contacts = await repository_contacts.get_all_contacts(current_user, db)
    return contacts[offset:][:limit]


@router.get("/read/{contact_id}", description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_by_id(contact_id, db: Session = Depends(get_db),
                    current_user: User = Depends(auth_service.get_current_user)):
    """
    Get a contact by its ID.

    Args:
        contact_id (int): The ID of the contact.
        db (Session): The database session.
        current_user (User): The current user.

    Returns:
        Contact: The requested contact.
    """
    contact = r.get(str(contact_id))
    if contact is None:
        contact = await repository_contacts.get_contact(contact_id, current_user, db)
        r.set(str(contact_id), json.dumps(contact))
        r.expire(str(contact), 3600)
        if contact is None:
            return 'Not found'
        return contact
    return json.loads(contact)


@router.put("/update/{contact_id}", description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def update_contact(contact_id, first_name: str = None, last_name: str = None, email: str = None,
                         phone: str = None, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    Update a contact by its ID.

    Args:
        contact_id (int): The ID of the contact.
        first_name (str, optional): Updated first name. Defaults to None.
        last_name (str, optional): Updated last name. Defaults to None.
        email (str, optional): Updated email. Defaults to None.
        phone (str, optional): Updated phone number. Defaults to None.
        db (Session): The database session.
        current_user (User): The current user.

    Returns:
        dict: Response confirming the update.
    """
    updated = await repository_contacts.put_contact(contact_id, first_name, last_name, email, phone, current_user, db)
    if updated is None:
        return "Not found"
    return {"message": "Contact updated successfully", "contact": updated}


@router.delete("/delete/{contact_id}", description='No more than 10 requests per minute',
               dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def delete_by_id(contact_id, current_user: User = Depends(auth_service.get_current_user),
                       db: Session = Depends(get_db)):
    """
    Delete a contact by its ID.

    Args:
        contact_id (int): The ID of the contact.
        current_user (User): The current user.
        db (Session): The database session.

    Returns:
        dict: Response confirming the deletion.
    """
    contact = await repository_contacts.del_contact(contact_id, current_user, db)
    if contact is None:
        return "Not found"
    return {"message": "Contact deleted successfully", "contact": contact}


@cache
@router.get("/search", description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def search_contact(first_name: Optional[str] = Query(default=None),
                         last_name: Optional[str] = Query(default=None),
                         email: Optional[str] = Query(default=None),
                         current_user: User = Depends(auth_service.get_current_user),
                         db: Session = Depends(get_db)):
    """
    Search for contacts by name or email.

    Args:
        first_name (str, optional): First name to search for. Defaults to None.
        last_name (str, optional): Last name to search for. Defaults to None.
        email (str, optional): Email to search for. Defaults to None.
        current_user (User): The current user.
        db (Session): The database session.

    Returns:
        List[Contact]: List of contacts matching the search criteria.
    """
    contacts = await repository_contacts.search(first_name, last_name, email, current_user, db)
    if contacts is None:
        return "Contact not found"
    return contacts


@cache
@router.get("/upcoming_birthdays", description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def upcoming_birthdays(current_user: User = Depends(auth_service.get_current_user),
                             db: Session = Depends(get_db)):
    """
    Get upcoming birthdays within the next week.

    Args:
        current_user (User): The current user.
        db (Session): The database session.

    Returns:
        List[Contact]: List of contacts with upcoming birthdays.
    """
    birthdays = await repository_contacts.birthdays(current_user, db)
    if not birthdays:
        return "No birthdays in upcoming week"
    return birthdays
