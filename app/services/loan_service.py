from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from app.models.loan_model import Loan
from app.schemas.loan_schema import LoanCreate, LoanExtend
from fastapi import HTTPException
from datetime import datetime, timedelta
from app.services.book_service import BookService
from app.services.user_service import UserService

class LoanService:
    def __init__(self, db: Session):
        self.db = db
        self.book_service = BookService(db)
        self.user_service = UserService(db)

    def issue_book(self, loan: LoanCreate) -> Loan:
        book = self.book_service.get_book(loan.book_id)
        if book.available_copies <= 0:
            raise HTTPException(status_code=400, detail="Book not available")
        self.user_service.get_user(loan.user_id) 
        
        db_loan = Loan(
            user_id=loan.user_id,
            book_id=loan.book_id,
            due_date=loan.due_date,
            status="ACTIVE"
        )
        book.available_copies -= 1
        self.db.add(db_loan)
        self.db.commit()
        self.db.refresh(db_loan)
        return db_loan

    def return_book(self, loan_id: int) -> Loan:
        db_loan = self.db.query(Loan).filter(Loan.id == loan_id).first()
        if not db_loan or db_loan.status != "ACTIVE":
            raise HTTPException(status_code=400, detail="Invalid loan")
        db_loan.status = "RETURNED"
        db_loan.return_date = datetime.utcnow()
        book = self.book_service.get_book(db_loan.book_id)
        book.available_copies += 1
        self.db.commit()
        self.db.refresh(db_loan)
        return db_loan

    def get_overdue_loans(self) -> list[dict]:
        current_time = datetime.utcnow()
        overdue_loans = self.db.query(Loan).options(
            joinedload(Loan.book),
            joinedload(Loan.user)
        ).filter(
            Loan.status == "ACTIVE",
            Loan.due_date < current_time
        ).all()

        return [
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

    def get_user_loans(self, user_id: int) -> list[Loan]:
        self.user_service.get_user(user_id)  # Will raise 404 if user not found
        loans = (
            self.db.query(Loan)
            .options(joinedload(Loan.book))
            .filter(Loan.user_id == user_id)
            .all()
        )
        return loans if loans else []

    def extend_loan(self, loan_id: int, extend: LoanExtend) -> Loan:
        db_loan = self.db.query(Loan).filter(Loan.id == id).first()
        if not db_loan:
            raise HTTPException(status_code=404, detail="Loan not found")
        if db_loan.status != "ACTIVE":
            raise HTTPException(status_code=400, detail="Only active loans can be extended")
        if db_loan.extensions_count >= 2:
            raise HTTPException(status_code=400, detail="Maximum extensions reached")
        if extend.extension_days <= 0:
            raise HTTPException(status_code=400, detail="Extension days must be positive")
        
        if db_loan.extensions_count == 0:
            db_loan.original_due_date = db_loan.original_due_date or db_loan.due_date
        
        extension_period = timedelta(days=extend.extension_days)
        new_due_date = db_loan.due_date + extension_period
        db_loan.due_date = new_due_date
        db_loan.extensions_count += 1

        self.db.commit()
        self.db.refresh(db_loan)
        return db_loan