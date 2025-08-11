from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas, services
from app.api import dependencies
from app.db.session import get_db

router = APIRouter()

@router.post("/", response_model=schemas.Siparis)
def siparis_olustur(
    siparis_data: schemas.SiparisCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user),
):
    """
    Giriş yapmış kullanıcının sepetinden yeni bir sipariş oluşturur.
    İşlem başarılı olursa sepeti temizler.
    """
    return services.siparis_service.create_order_from_cart(
        db=db, kullanici=current_user, siparis_data=siparis_data
    )

@router.get("/", response_model=List[schemas.Siparis])
def kullanici_siparislerini_listele(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user),
):
    """
    Giriş yapmış kullanıcının tüm geçmiş siparişlerini listeler.
    """
    return services.siparis_service.get_kullanici_siparisleri(
        db=db, kullanici_id=current_user.id
    )