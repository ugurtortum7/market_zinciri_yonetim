from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import schemas, models, services
from app.api import dependencies
from app.db.session import get_db

router = APIRouter()

@router.post("/", response_model=schemas.Stok)
def create_stok_kaydi(
    stok: schemas.StokCreate,
    db: Session = Depends(get_db),
    current_manager: models.User = Depends(dependencies.get_current_manager_user)
):
    """
    Bir lokasyona yeni bir ürün için stok kaydı oluşturur.
    Örn: Depoya yeni gelen bir ürünün ilk defa stoğa girilmesi.
    Sadece Yöneticiler erişebilir.
    """
    db_stok = services.stok_service.get_stok_by_lokasyon_and_urun(
        db, lokasyon_id=stok.lokasyon_id, urun_id=stok.urun_id
    )
    if db_stok:
        raise HTTPException(
            status_code=400,
            detail="Bu lokasyonda bu ürün için zaten bir stok kaydı mevcut."
        )
    return services.stok_service.create_stok(db=db, stok=stok)

@router.get("/", response_model=List[schemas.Stok])
def read_stoklar(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """
    Sistemdeki tüm stok kayıtlarını detaylı olarak listeler.
    Giriş yapmış tüm kullanıcılar erişebilir.
    """
    return services.stok_service.get_stoklar(db=db)

@router.put("/{stok_id}/kritik-seviye", response_model=schemas.Stok)
def set_kritik_seviye(
    stok_id: int,
    kritik_seviye_data: schemas.StokUpdateKritikSeviye,
    db: Session = Depends(get_db),
    current_manager: models.User = Depends(dependencies.get_current_manager_user)
):
    """
    Belirli bir stok kaydı için kritik seviyeyi belirler veya günceller.
    Sadece Yöneticiler erişebilir.
    """
    stok = services.stok_service.get_stok_by_id(db, stok_id=stok_id)
    if not stok:
        raise HTTPException(status_code=404, detail="Stok kaydı bulunamadı.")
    
    if stok.lokasyon.tip != "SUPERMARKET":
        raise HTTPException(
            status_code=400,
            detail="Kritik seviye sadece 'SUPERMARKET' tipindeki lokasyonlar için ayarlanabilir."
        )

    return services.stok_service.update_kritik_seviye(
        db=db, stok=stok, kritik_seviye=kritik_seviye_data.kritik_seviye
    )