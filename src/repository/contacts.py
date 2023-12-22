from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.database.models import Contact, User
from src.schemas import ContactBase, ContactResponse, UserModel, UserDb, UserResponse, TokenModel


async def get_contacts(skip: int, limit: int, user: User, db: Session) -> List[Contact]:
    return db.query(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit).all()


async def get_contact(contact_id: int, user: User, db: Session) -> Contact:
    return db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()


async def create_contact(body: ContactBase, user: User, db: Session) -> Contact:
    contact = Contact(name=body.name, user_id=user.id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def remove_contact(contact_id: int, user: User, db: Session) -> Contact | None:
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def update_contact(contact_id: int, body: ContactResponse, user: User, db: Session) -> Contact | None:
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if contact:
        contact.firstname = body.firstname
        contact.lastname = body.lastname
        contact.email = body.email
        contact.phone = body.phone
        contact.birthdate = body.birthdate
        contact.additional_data = body.additional_data
        db.commit()
    return contact
