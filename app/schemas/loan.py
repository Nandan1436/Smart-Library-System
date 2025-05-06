from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .book import BookInLoan
from .user import UserInLoan

class LoanCreate(BaseModel):
    user_id: int
    book_id: int
    due_date: datetime

class LoanReturn(BaseModel):
    loan_id: int

class LoanExtend(BaseModel):
    extension_days: int

class LoanHistoryResponse(BaseModel):
    id: int
    book: BookInLoan
    issue_date: datetime
    due_date: datetime
    return_date: Optional[datetime]
    status: str

    class Config:
        orm_mode = True

class OverdueLoanResponse(BaseModel):
    id: int
    user: UserInLoan
    book: BookInLoan
    issue_date: datetime
    due_date: datetime
    days_overdue: int

    class Config:
        orm_mode = True

class LoanIssueResponse(BaseModel):
    id: int
    user_id: int
    book_id: int 
    issue_date: datetime
    due_date: datetime
    status: str

    class Config:
        orm_mode = True

class LoanReturnResponse(BaseModel):
    id: int
    user_id: int
    book_id: int 
    issue_date: datetime
    due_date: datetime
    return_date: datetime
    status: str

    class Config: 
        orm_mode = True

class LoanExtensionResponse(BaseModel):
    id: int
    user_id: int
    book_id: int
    issue_date: datetime
    original_due_date: Optional[datetime] = None
    extended_due_date: Optional[datetime] = None
    status: str
    extensions_count: Optional[int] = 0

    class Config:
        orm_mode = True