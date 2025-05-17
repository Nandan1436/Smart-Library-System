from database import Base, engine
from app.models.user_model import User
from app.models.book_model import Book
from app.models.loan_model import Loan

# Create all tables defined in the models
Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")