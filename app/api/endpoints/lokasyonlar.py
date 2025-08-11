from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app import schemas, models
from app.db.session import get_db
from app.services import lokasyon_service
from app.api.dependencies import get_current_manager_user

router = APIRouter()

@router.post("/", response_model=schemas.Lokasyon)
def create_lokasyon(
    lokasyon: schemas.LokasyonCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_manager_user)
):
    """
    Yeni bir lokasyon oluşturur. Sadece Yöneticiler erişebilir.
    """
    return lokasyon_service.create_lokasyon(db=db, lokasyon=lokasyon)


@router.get("/", response_model=List[schemas.Lokasyon])
def read_lokasyonlar(
    db: Session = Depends(get_db),
):
    """
    Tüm lokasyonları listeler.
    """
    lokasyonlar = lokasyon_service.get_lokasyonlar(db=db)
    return lokasyonlar