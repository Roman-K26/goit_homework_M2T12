from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.schemas import ContactBase, ContactResponse, UserModel, UserDb, UserResponse, TokenModel
from src.repository import contacts as repository_contacts
from src.services.auth import auth_service

router = APIRouter(prefix='/contacts', tags=["contacts"])


@router.get("/", response_model=List[ContactResponse], description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))], tags=["contacts"])
async def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                     current_user: User = Depends(auth_service.get_current_user)):
    """
    Retrieves a list of contacts for the current user with specified pagination parameters.

    Parameters:
        skip (int): The number of contacts to skip.
        limit (int): The maximum number of contacts to return.
        db (Session): The database session.
        current_user (User): The current authenticated user.

    Returns:
        List[ContactResponse]: A list of contacts.
    """
    contacts = await repository_contacts.get_contacts(skip, limit, current_user, db)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse, description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))], tags=["contacts"])
async def read_contact(contact_id: int, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    Retrieves a specific contact for the current user.

    Parameters:
        contact_id (int): The ID of the contact to retrieve.
        db (Session): The database session.
        current_user (User): The current authenticated user.

    Raises:
        HTTPException: If the contact is not found.

    Returns:
        ContactResponse: The requested contact.
    """
    contact = await repository_contacts.get_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED, description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))], tags=["contacts"])
async def create_contact(body: ContactBase, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    Creates a new contact for the current user.

    Parameters:
        body (ContactBase): The data for the new contact.
        db (Session): The database session.
        current_user (User): The current authenticated user.

    Returns:
        ContactResponse: The newly created contact.
    """
    return await repository_contacts.create_contact(body, current_user, db)


@router.put("/{contact_id}", response_model=ContactResponse, tags=["contacts"])
async def update_contact(body: ContactBase, contact_id: int, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    Updates an existing contact for the current user.

    Parameters:
        body (ContactBase): The updated data for the contact.
        contact_id (int): The ID of the contact to update.
        db (Session): The database session.
        current_user (User): The current authenticated user.

    Raises:
        HTTPException: If the contact is not found.

    Returns:
        ContactResponse: The updated contact.
    """
    contact = await repository_contacts.update_contact(contact_id, body, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse, tags=["contacts"])
async def remove_contact(contact_id: int, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    Removes a contact for the current user.

    Parameters:
        contact_id (int): The ID of the contact to remove.
        db (Session): The database session.
        current_user (User): The current authenticated user.

    Raises:
        HTTPException: If the contact is not found.

    Returns:
        ContactResponse: The removed contact.
    """
    contact = await repository_contacts.remove_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact