from fastapi import FastAPI
from app.routes import book_route, loan_route, stats_route
from app.routes import user_route

app = FastAPI(title="Smart Library System")

app.include_router(user_route.router)
app.include_router(book_route.router)
app.include_router(loan_route.router)
app.include_router(stats_route.router)

@app.get("/")
def read_root():
    return {"message": "Smart Library System API"}