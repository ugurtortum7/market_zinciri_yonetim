# app/api/endpoints/sepet_api.py

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas, services
from app.api import dependencies
from app.db.session import get_db

router = APIRouter()

@router.get("/", response_model=schemas.Sepet)
def sepeti_getir(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """
    O an giriş yapmış olan kullanıcının sepetini, içindeki ürünlerle
    birlikte getirir. Kullanıcının sepeti yoksa, boş bir sepet oluşturur.
    """
    return services.sepet_service.get_veya_create_kullanici_sepeti(
        db=db, kullanici_id=current_user.id
    )

@router.post("/urunler", response_model=schemas.Sepet)
def sepete_urun_ekle(
    urun_data: schemas.SepetUrunuCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """
    Kullanıcının sepetine yeni bir ürün ekler veya mevcut ürünün miktarını artırır.
    İşlem sonrası sepetin son halini döndürür.
    """
    return services.sepet_service.sepete_urun_ekle(
        db=db, kullanici_id=current_user.id, urun_data=urun_data
    )

@router.put("/urunler", response_model=schemas.Sepet)
def sepet_urun_miktarini_guncelle(
    urun_data: schemas.SepetUrunuUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """
    Sepetteki bir ürünün miktarını belirtilen yeni değerle günceller.
    Eğer yeni miktar 0 ise, ürün sepetten kaldırılır.
    """
    return services.sepet_service.sepet_urun_miktarini_guncelle(
        db=db, 
        kullanici_id=current_user.id, 
        urun_id=urun_data.urun_id, 
        yeni_miktar=urun_data.yeni_miktar
    )

@router.delete("/urunler/{urun_id}", response_model=schemas.Sepet)
def sepetten_urunu_sil(
    urun_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """
    Belirtilen ürünü sepetten tamamen kaldırır.
    Bu, miktarı 0'a güncellemekle aynı işi yapar.
    """
    return services.sepet_service.sepet_urun_miktarini_guncelle(
        db=db, kullanici_id=current_user.id, urun_id=urun_id, yeni_miktar=0
    )

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def sepeti_temizle(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """
    Kullanıcının sepetindeki tüm ürünleri temizler.
    """
    services.sepet_service.sepeti_temizle(db=db, kullanici_id=current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)