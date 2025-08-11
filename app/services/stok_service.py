from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from app.models.stok import Stok
from app.schemas.stok import StokCreate

def get_stok_by_lokasyon_and_urun(db: Session, lokasyon_id: int, urun_id: int) -> Optional[Stok]:
    """
    Belirli bir lokasyon ve ürüne ait stok kaydını bulur.
    """
    return db.query(Stok).filter(Stok.lokasyon_id == lokasyon_id, Stok.urun_id == urun_id).first()

def create_stok(db: Session, stok: StokCreate) -> Stok:
    """
    Yeni bir stok kaydı oluşturur.
    """
    db_stok = Stok(**stok.model_dump())
    db.add(db_stok)
    db.commit()
    db.refresh(db_stok)
    return db_stok

def get_stoklar(db: Session) -> List[Stok]:
    """
    Tüm stok kayıtlarını, ilişkili lokasyon ve ürün bilgileriyle birlikte getirir.
    joinedload, N+1 problemini önlemek için verimli bir sorgulama yöntemidir.
    """
    return db.query(Stok).options(joinedload(Stok.lokasyon), joinedload(Stok.urun)).all()

def get_stok_by_id(db: Session, stok_id: int) -> Optional[Stok]:
    """
    Verilen ID'ye sahip tek bir stok kaydını bulur.
    """
    return db.query(Stok).filter(Stok.id == stok_id).first()

def update_kritik_seviye(db: Session, stok: Stok, kritik_seviye: int) -> Stok:
    """
    Mevcut bir stok kaydının kritik seviyesini günceller.
    """
    stok.kritik_seviye = kritik_seviye
    db.commit()
    db.refresh(stok)
    return stok