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