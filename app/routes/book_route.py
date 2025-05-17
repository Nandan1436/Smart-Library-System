from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.models.book_model import Book
from app.schemas.book_schema import BookCreate, BookResponse, BookUpdate
from app.services.book_service import BookService
from app.database import get_db
from typing import Optional, List

router = APIRouter(prefix="/api/books", tags=["Books"])

def get_book_service(db: Session = Depends(get_db)) -> BookService:
    return BookService(db)

@router.post("/", response_model=BookResponse, status_code=201)
def create_book(book: BookCreate, book_service: BookService = Depends(get_book_service)):
    return book_service.create_book(book)

@router.get("/{id}", response_model=BookResponse)
def get_book(id: int, book_service: BookService = Depends(get_book_service)):
    return book_service.get_book(id)

@router.get("/", response_model=List[BookResponse])
def search_books(
    search: Optional[str] = Query(None),
    book_service: BookService = Depends(get_book_service)
):
    return book_service.search_books(search)

@router.put("/{id}", response_model=BookResponse)
def update_book(id: int, book: BookUpdate, book_service: BookService = Depends(get_book_service)):
    return book_service.update_book(id, book)

@router.delete("/{id}", status_code=204)
def delete_book(id: int, book_service: BookService = Depends(get_book_service)):
    book_service.delete_book(id)
    return None