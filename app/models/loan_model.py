from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base

class Loan(Base):
    __tablename__ = 'loans'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False, index=True)
    issue_date = Column(DateTime, server_default=func.now(), nullable=False)
    due_date = Column(DateTime, nullable=False)
    return_date = Column(DateTime)
    status = Column(String(20), nullable=False)
    extensions_count = Column(Integer, default=0)
    original_due_date = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    
    book = relationship("Book", back_populates="loans")
    user = relationship("User", back_populates="loans")

