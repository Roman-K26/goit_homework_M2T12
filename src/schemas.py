from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr


class ContactBase(BaseModel):
    firstname: str = Field(max_length=100)
    lastname: str = Field(max_length=100)
    email: str = Field(max_length=100)
    phone: str = Field(max_length=100)
    birthdate: str = Field(max_length=100)
    additional_data: str = Field(max_length=200)



class ContactResponse(ContactBase):
    id: int


    class Config:
        orm_mode = True


class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=16)
    email: str
    password: str = Field(min_length=6, max_length=10)


class UserDb(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    avatar: str

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RequestEmail(BaseModel):
    email: EmailStr