from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session,joinedload
from models.loan import Loan
from models.book import Book
from models.user import User
from schemas.loan import LoanCreate, LoanIssueResponse, LoanExtensionResponse, LoanHistoryResponse, LoanReturnResponse, OverdueLoanResponse, LoanExtend
from database import get_db
from datetime import datetime,timedelta
from sqlalchemy import and_

router = APIRouter(prefix="/api/loans", tags=["Loans"])

@router.post("/", response_model=LoanIssueResponse, status_code=201)
def issue_book(loan: LoanCreate, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == loan.book_id).first()
    if not book or book.available_copies <= 0:
        raise HTTPException(status_code=400, detail="Book not available")
    user = db.query(User).filter(User.id == loan.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_loan = Loan(
        user_id=loan.user_id,
        book_id=loan.book_id,
        due_date=loan.due_date,
        status="ACTIVE"
    )
    book.available_copies -= 1
    db.add(db_loan)
    db.commit()
    db.refresh(db_loan)
    return db_loan

@router.post("/returns", response_model=LoanReturnResponse)
def return_book(loan_id: int, db: Session = Depends(get_db)):
    db_loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not db_loan or db_loan.status != "ACTIVE":
        raise HTTPException(status_code=400, detail="Invalid loan")
    db_loan.status = "RETURNED"
    db_loan.return_date = datetime.utcnow()
    book = db.query(Book).filter(Book.id == db_loan.book_id).first()
    book.available_copies += 1
    db.commit()
    db.refresh(db_loan)
    return db_loan

@router.get("/overdue", response_model=list[OverdueLoanResponse])
def get_overdue_loans(db: Session = Depends(get_db)):
    current_time = datetime.utcnow()
    overdue_loans = db.query(Loan).options(
        joinedload(Loan.book),
        joinedload(Loan.user)
    ).filter(
        Loan.status == "ACTIVE",
        Loan.due_date < current_time
    ).all()

    result = [
        {
            "id": loan.id,
            "user": {
                "id": loan.user.id,
                "name": loan.user.name,
                "email": loan.user.email,
            },
            "book": {
                "id": loan.book.id,
                "title": loan.book.title,
                "author": loan.book.author,
            },
            "issue_date": loan.issue_date,
            "due_date": loan.due_date,
            "days_overdue": (current_time - loan.due_date).days
        }
        for loan in overdue_loans
    ]

    return result

@router.get("/{user_id}", response_model=list[LoanHistoryResponse])
def get_user_loans(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    loans = (
        db.query(Loan)
        .join(Book, Loan.book_id == Book.id)
        .filter(Loan.user_id == user_id)
        .all()
    )
    if not loans:
        return []
    return loans



@router.put("/{id}/extend", response_model=LoanExtensionResponse)
def extend_loan(id: int, extend: LoanExtend, db: Session = Depends(get_db)):
    db_loan = db.query(Loan).filter(Loan.id == id).first()
    if not db_loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    if db_loan.status != "ACTIVE":
        raise HTTPException(status_code=400, detail="Only active loans can be extended")
    if db_loan.extensions_count >= 2:
        raise HTTPException(status_code=400, detail="Maximum extensions reached")
    
    extension_period = timedelta(days=extend.extension_days)
    new_due_date = db_loan.due_date + extension_period
    db_loan.due_date = new_due_date
    db_loan.extensions_count += 1
    db_loan.extended_due_date = new_due_date
    if db_loan.extensions_count == 1:
        db_loan.original_due_date = db_loan.original_due_date or db_loan.due_date
    
    db.commit()
    db.refresh(db_loan)
    return db_loan