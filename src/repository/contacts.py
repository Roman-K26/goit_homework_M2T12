"""Module to handle contact-related operations."""

from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from src.database.models import Contact, User
from src.schemas import ContactBase, ContactResponse, UserModel, UserDb, UserResponse, TokenModel


async def get_contacts(skip: int, limit: int, user: User, db: Session) -> List[Contact]:
    """
    Retrieve a list of contacts for a specific user.

    Args:
        skip (int): The number of contacts to skip.
        limit (int): The maximum number of contacts to retrieve.
        user (User): The user for whom contacts are retrieved.
        db (Session): The database session.

    Returns:
        List[Contact]: A list of contacts for the specified user.
    """
    return db.query(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit).all()


async def get_contact(contact_id: int, user: User, db: Session) -> Contact:
    """
    Retrieve a specific contact for a user.

    Args:
        contact_id (int): The ID of the contact to retrieve.
        user (User): The user for whom the contact is retrieved.
        db (Session): The database session.

    Returns:
        Contact: The specified contact for the user.
    """
    return db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()


async def create_contact(body: ContactBase, user: User, db: Session) -> Contact:
    """
    Create a new contact for a user.

    Args:
        body (ContactBase): The data for creating a new contact.
        user (User): The user for whom the contact is created.
        db (Session): The database session.

    Returns:
        Contact: The newly created contact.
    """
    contact = Contact(firstname=body.firstname, lastname=body.lastname, email=body.email, phone=body.phone, birthdate=body.birthdate, additional_data=body.additional_data, user_id=user.id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def remove_contact(contact_id: int, user: User, db: Session) -> Contact | None:
    """
    Remove a contact for a user.

    Args:
        contact_id (int): The ID of the contact to remove.
        user (User): The user for whom the contact is removed.
        db (Session): The database session.

    Returns:
        Contact | None: The removed contact or None if not found.
    """
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def update_contact(contact_id: int, body: ContactResponse, user: User, db: Session) -> Contact | None:
    """
    Update a contact for a user.

    Args:
        contact_id (int): The ID of the contact to update.
        body (ContactResponse): The updated data for the contact.
        user (User): The user for whom the contact is updated.
        db (Session): The database session.

    Returns:
        Contact | None: The updated contact or None if not found.
    """
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
