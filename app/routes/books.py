from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from models.book import Book
from schemas.book import BookCreate, BookResponse, BookUpdate
from database import get_db
from typing import Optional

router = APIRouter(prefix="/api/books", tags=["Books"])

@router.post("/", response_model=BookResponse, status_code=201)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    db_book = Book(**book.dict(), available_copies=book.copies)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@router.get("/{id}", response_model=BookResponse)
def get_book(id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.get("/", response_model=list[BookResponse])
def search_books(
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Book)
    if search:
        query = query.filter(
            or_(
                Book.title.ilike(f"%{search}%"),
                Book.author.ilike(f"%{search}%"),
                
            )
        )
    return query.all()

@router.put("/{id}", response_model=BookResponse)
def update_book(id: int, book: BookUpdate, db: Session = Depends(get_db)):
    db_book = db.query(Book).filter(Book.id == id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    for key, value in book.dict(exclude_unset=True).items():
        setattr(db_book, key, value)
    if book.copies is not None:
        db_book.available_copies = min(db_book.available_copies, book.copies)
    db.commit()
    db.refresh(db_book)
    return db_book

@router.delete("/{id}", status_code=204)
def delete_book(id: int, db: Session = Depends(get_db)):
    db_book = db.query(Book).filter(Book.id == id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(db_book)
    db.commit()
    return None