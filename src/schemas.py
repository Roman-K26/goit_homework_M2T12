from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field



class ContactBase(BaseModel):
    firstname: str = Field(max_length=100)
    lastname: str = Field(max_length=100)
    email: str = Field(max_length=100)
    phone: str = Field(max_length=100)
    birthdate: str = Field(max_length=100)
    additional_data: str = Field(max_length=200)



class ContactResponse(ContactBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True