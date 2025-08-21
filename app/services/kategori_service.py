# app/services/kategori_service.py
from sqlalchemy.orm import Session
from app.models.kategori import Kategori
from app.schemas.kategori import KategoriCreate

def get_kategori_by_ad(db: Session, ad: str):
    return db.query(Kategori).filter(Kategori.ad == ad).first()

def get_kategoriler(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Kategori).offset(skip).limit(limit).all()

def create_kategori(db: Session, kategori: KategoriCreate):
    db_kategori = Kategori(ad=kategori.ad)
    db.add(db_kategori)
    db.commit()
    db.refresh(db_kategori)
    return db_kategori