from pydantic import BaseModel
from typing import List

class PopularBookResponse(BaseModel):
    book_id: int
    title: str
    author: str
    borrow_count: int

class ActiveUserResponse(BaseModel):
    user_id: int
    name: str
    books_borrowed: int
    current_borrows: int

class OverviewResponse(BaseModel):
    total_books: int
    total_users: int
    books_available: int
    books_borrowed: int
    overdue_loans: int
    loans_today: int
    returns_today: int