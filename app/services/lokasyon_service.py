from sqlalchemy.orm import Session
from typing import List

from app.models.lokasyon import Lokasyon
from app.schemas.lokasyon import LokasyonCreate

def create_lokasyon(db: Session, lokasyon: LokasyonCreate) -> Lokasyon:
    """
    Veritabanında yeni bir lokasyon oluşturur.
    """
    db_lokasyon = Lokasyon(**lokasyon.model_dump())
    db.add(db_lokasyon)
    db.commit()
    db.refresh(db_lokasyon)
    return db_lokasyon

def get_lokasyonlar(db: Session) -> List[Lokasyon]:
    """
    Veritabanındaki tüm lokasyonları listeler.
    """
    return db.query(Lokasyon).all()