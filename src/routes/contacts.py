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
    return await repository_contacts.create_contact(contact, current_user, db)


@cache
@router.get("/all", description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_all(limit: int = 10, offset: int = 0,
                  db: Session = Depends(get_db),
                  current_user: User = Depends(auth_service.get_current_user)):
    contacts = await repository_contacts.get_all_contacts(current_user, db)
    return contacts[offset:][:limit]


@router.get("/read/{contact_id}", description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_by_id(contact_id, db: Session = Depends(get_db),
                    current_user: User = Depends(auth_service.get_current_user)):
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
    updated = await repository_contacts.put_contact(contact_id, first_name, last_name, email, phone, current_user, db)
    if updated is None:
        return "Not found"
    return {"message": "Contact updated successfully", "contact": updated}


@router.delete("/delete/{contact_id}", description='No more than 10 requests per minute',
               dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def delete_by_id(contact_id,
                       current_user: User = Depends(auth_service.get_current_user),
                       db: Session = Depends(get_db)):
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
    contacts = await repository_contacts.search(first_name, last_name, email, current_user, db)
    if contacts is None:
        return "Contact not found"
    return contacts


@cache
@router.get("/upcoming_birthdays", description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def upcoming_birthdays(current_user: User = Depends(auth_service.get_current_user),
                             db: Session = Depends(get_db)):
    birthdays = await repository_contacts.birthdays(current_user, db)
    if not birthdays:
        return "No birthdays in upcoming week"
    return birthdays
