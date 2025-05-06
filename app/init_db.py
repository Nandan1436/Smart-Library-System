from database import Base, engine
from models.user import User
from models.book import Book
from models.loan import Loan

# Create all tables defined in the models
Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")