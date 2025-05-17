from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BookCreate(BaseModel):
    title: str
    author: str
    isbn: str
    copies: int

class BookUpdate(BaseModel):
    copies: Optional[int]
    available_copies: Optional[int]

class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    isbn: str
    copies: int
    available_copies: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class BookInLoan(BaseModel):
    id: int
    title: str
    author: str

    class Config:
        orm_mode = True