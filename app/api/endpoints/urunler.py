# app/api/endpoints/urunler.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import schemas, models, services
from app.api import dependencies
from app.db.session import get_db

router = APIRouter()

@router.post("/", response_model=schemas.Urun)
def create_urun(
    urun: schemas.UrunCreate,
    db: Session = Depends(get_db),
    current_manager: models.User = Depends(dependencies.get_current_manager_user)
):
    """
    Yeni bir ürün oluşturur. Sadece Yöneticiler erişebilir.
    Aynı SKU'ya sahip başka bir ürün varsa hata verir.
    """
    db_urun = services.urun_service.get_urun_by_sku(db, sku=urun.sku)
    if db_urun:
        raise HTTPException(status_code=400, detail=f"Bu SKU ({urun.sku}) zaten kayıtlı.")
    
    return services.urun_service.create_urun(db=db, urun=urun)

@router.put("/{urun_id}", response_model=schemas.Urun)
def update_urun(
    urun_id: int,
    urun_in: schemas.UrunUpdate,
    db: Session = Depends(get_db),
    current_manager: models.User = Depends(dependencies.get_current_manager_user)
):
    """

    Belirtilen ID'ye sahip bir ürünü günceller. Sadece Yöneticiler erişebilir.
    """
    urun = services.urun_service.get_urun(db, urun_id=urun_id)
    if not urun:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı.")
    
    # Eğer yeni bir SKU gönderildiyse, bu SKU'nun başka bir ürüne ait olup olmadığını kontrol et
    if urun_in.sku and urun_in.sku != urun.sku:
        db_urun_by_sku = services.urun_service.get_urun_by_sku(db, sku=urun_in.sku)
        if db_urun_by_sku:
            raise HTTPException(status_code=400, detail=f"Bu SKU ({urun_in.sku}) zaten başka bir ürüne ait.")

    urun = services.urun_service.update_urun(db=db, db_obj=urun, obj_in=urun_in)
    return urun

@router.get("/", response_model=List[schemas.Urun])
def read_urunler(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """
    Sistemdeki tüm ürünleri listeler.
    Giriş yapmış tüm kullanıcılar erişebilir.
    """
    urunler = services.urun_service.get_urunler(db=db)
    return urunler