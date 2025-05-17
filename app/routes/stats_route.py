from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func,case
from app.models.loan_model import Loan
from app.models.book_model import Book
from app.models.user_model import User
from app.schemas.stat_schema import PopularBookResponse, ActiveUserResponse, OverviewResponse
from app.database import get_db
from datetime import datetime, date

router = APIRouter(prefix="/api/stats", tags=["Statistics"])

@router.get("/books/popular", response_model=list[PopularBookResponse])
def get_popular_books(db: Session = Depends(get_db)):
    popular_books = (
        db.query(
            Book.id.label("book_id"),
            Book.title,
            Book.author,
            func.count(Loan.id).label("borrow_count")
        )
        .join(Loan, Loan.book_id == Book.id)
        .group_by(Book.id, Book.title, Book.author)
        .order_by(func.count(Loan.id).desc())
        .limit(3)
        .all()
    )
    return [
        {"book_id": book.book_id, "title": book.title, "author": book.author, "borrow_count": book.borrow_count}
        for book in popular_books
    ]


@router.get("/users/active", response_model=list[ActiveUserResponse])
def get_active_users(db: Session = Depends(get_db)):
    active_users = (
        db.query(
            User.id.label("user_id"),
            User.name,
            func.count(Loan.id).label("books_borrowed"),
            func.sum(
                case(
                    (Loan.status == "ACTIVE", 1),
                    else_=0
                )
            ).label("current_borrows")
        )
        .join(Loan, Loan.user_id == User.id)
        .group_by(User.id, User.name)
        .order_by(func.count(Loan.id).desc())
        .limit(4)
        .all()
    )
    return [
        {
            "user_id": user.user_id,
            "name": user.name,
            "books_borrowed": user.books_borrowed,
            "current_borrows": user.current_borrows or 0
        }
        for user in active_users
    ]
@router.get("/overview", response_model=OverviewResponse)
def get_overview_stats(db: Session = Depends(get_db)):
    total_books = db.query(func.count(Book.id)).scalar()
    total_users = db.query(func.count(User.id)).scalar()
    books_available = db.query(func.sum(Book.available_copies)).scalar() or 0
    books_borrowed = db.query(func.count(Loan.id)).filter(Loan.status == "ACTIVE").scalar()
    overdue_loans = db.query(func.count(Loan.id)).filter(
        Loan.status == "ACTIVE",
        Loan.due_date < datetime.utcnow()
    ).scalar()
    today = date.today()
    loans_today = db.query(func.count(Loan.id)).filter(
        func.date(Loan.issue_date) == today
    ).scalar()
    returns_today = db.query(func.count(Loan.id)).filter(
        func.date(Loan.return_date) == today
    ).scalar()
    return {
        "total_books": total_books,
        "total_users": total_users,
        "books_available": books_available,
        "books_borrowed": books_borrowed,
        "overdue_loans": overdue_loans,
        "loans_today": loans_today,
        "returns_today": returns_today
    }