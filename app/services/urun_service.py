# app/services/urun_service.py

from sqlalchemy.orm import Session
from typing import List, Optional

from app import schemas # schemas'ı import ediyoruz
from app.models.urun import Urun
from app.schemas.urun import UrunCreate, UrunUpdate # UrunUpdate'i import ediyoruz

def get_urun_by_sku(db: Session, sku: str) -> Optional[Urun]:
    """
    Verilen SKU'ya sahip bir ürün olup olmadığını kontrol eder.
    """
    return db.query(Urun).filter(Urun.sku == sku).first()

def get_urun(db: Session, urun_id: int) -> Optional[Urun]:
    """
    Verilen ID'ye sahip ürünü veritabanından getirir.
    """
    return db.query(Urun).filter(Urun.id == urun_id).first()

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

def update_urun(db: Session, db_obj: Urun, obj_in: UrunUpdate) -> Urun:
    """
    Mevcut bir ürünü, gelen yeni verilerle günceller.
    Sadece gönderilen alanlar güncellenir.
    """
    obj_data = obj_in.model_dump(exclude_unset=True)
    for field in obj_data:
        setattr(db_obj, field, obj_data[field])
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj