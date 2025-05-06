from fastapi import FastAPI
from routes import users, books, loans, stats

app = FastAPI(title="Smart Library System")

app.include_router(users.router)
app.include_router(books.router)
app.include_router(loans.router)
app.include_router(stats.router)

@app.get("/")
def read_root():
    return {"message": "Smart Library System API"}