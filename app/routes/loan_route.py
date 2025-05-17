from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.loan_schema import LoanCreate, LoanIssueResponse, LoanExtensionResponse, LoanHistoryResponse, LoanReturnResponse, OverdueLoanResponse, LoanExtend
from app.database import get_db
from app.services.loan_service import LoanService

router = APIRouter(prefix="/api/loans", tags=["Loans"])

def get_loan_service(db: Session = Depends(get_db)) -> LoanService:
    return LoanService(db)

@router.post("/", response_model=LoanIssueResponse, status_code=201)
def issue_book(loan: LoanCreate, loan_service: LoanService = Depends(get_loan_service)):
    return loan_service.issue_book(loan)

@router.post("/returns", response_model=LoanReturnResponse)
def return_book(loan_id: int, loan_service: LoanService = Depends(get_loan_service)):
    return loan_service.return_book(loan_id)

@router.get("/overdue", response_model=list[OverdueLoanResponse])
def get_overdue_loans(loan_service: LoanService = Depends(get_loan_service)):
    return loan_service.get_overdue_loans()

@router.get("/{user_id}", response_model=list[LoanHistoryResponse])
def get_user_loans(user_id: int, loan_service: LoanService = Depends(get_loan_service)):
    return loan_service.get_user_loans(user_id)

@router.put("/{id}/extend", response_model=LoanExtensionResponse)
def extend_loan(id: int, extend: LoanExtend, loan_service: LoanService = Depends(get_loan_service)):
    return loan_service.extend_loan(id, extend)