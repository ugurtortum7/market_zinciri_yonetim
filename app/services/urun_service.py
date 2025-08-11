from sqlalchemy.orm import Session
from typing import List

from app.models.urun import Urun
from app.schemas.urun import UrunCreate

def get_urun_by_sku(db: Session, sku: str) -> Urun | None:
    """
    Verilen SKU'ya sahip bir ürün olup olmadığını kontrol eder.
    """
    return db.query(Urun).filter(Urun.sku == sku).first()

def create_urun(db: Session, urun: UrunCreate) -> Urun:
    """
    Veritabanında yeni bir ürün oluşturur.
    """
    db_urun = Urun(**urun.model_dump())
    db.add(db_urun)
    db.commit()
    db.refresh(db_urun)
    return db_urun

def get_urunler(db: Session) -> List[Urun]:
    """
    Veritabanındaki tüm ürünleri listeler.
    """
    return db.query(Urun).all()