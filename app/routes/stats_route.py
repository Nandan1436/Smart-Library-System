from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.stat_schema import PopularBookResponse, ActiveUserResponse, OverviewResponse
from app.database import get_db
from app.services.stat_service import StatService

router = APIRouter(prefix="/api/stats", tags=["Statistics"])

# Dependency to inject StatService
def get_stat_service(db: Session = Depends(get_db)) -> StatService:
    return StatService(db)

@router.get("/books/popular", response_model=list[PopularBookResponse])
def get_popular_books(stat_service: StatService = Depends(get_stat_service)):
    return stat_service.get_popular_books()

@router.get("/users/active", response_model=list[ActiveUserResponse])
def get_active_users(stat_service: StatService = Depends(get_stat_service)):
    return stat_service.get_active_users()

@router.get("/overview", response_model=OverviewResponse)
def get_overview_stats(stat_service: StatService = Depends(get_stat_service)):
    return stat_service.get_overview_stats()