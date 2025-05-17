from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.book_model import Book
from app.schemas.book_schema import BookCreate, BookUpdate
from fastapi import HTTPException
from typing import Optional

class BookService:
    def __init__(self, db: Session):
        self.db = db

    def create_book(self, book: BookCreate) -> Book:
        db_book = Book(**book.dict(), available_copies=book.copies)
        self.db.add(db_book)
        self.db.commit()
        self.db.refresh(db_book)
        return db_book

    def get_book(self, book_id: int) -> Book:
        book = self.db.query(Book).filter(Book.id == book_id).first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        return book

    def search_books(self, search: Optional[str] = None) -> list[Book]:
        query = self.db.query(Book)
        if search:
            query = query.filter(
                or_(
                    Book.title.ilike(f"%{search}%"),
                    Book.author.ilike(f"%{search}%"),
                )
            )
        return query.all()

    def update_book(self, book_id: int, book: BookUpdate) -> Book:
        db_book = self.db.query(Book).filter(Book.id == book_id).first()
        if not db_book:
            raise HTTPException(status_code=404, detail="Book not found")
        
        current_copies = db_book.copies
        current_available = db_book.available_copies

        for key, value in book.dict(exclude_unset=True).items():
            setattr(db_book, key, value)

        new_copies = db_book.copies if book.copies is not None else current_copies
        new_available = db_book.available_copies if book.available_copies is not None else current_available

        if new_available > new_copies:
            raise HTTPException(status_code=400, detail="Available copies cannot exceed total copies")
 
        if book.available_copies is None and book.copies is not None:
            db_book.available_copies = min(current_available, new_copies)

        self.db.commit()
        self.db.refresh(db_book)
        return db_book

    def delete_book(self, book_id: int) -> None:
        db_book = self.db.query(Book).filter(Book.id == book_id).first()
        if not db_book:
            raise HTTPException(status_code=404, detail="Book not found")
        self.db.delete(db_book)
        self.db.commit()