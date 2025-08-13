from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas, services
from app.api import dependencies
from app.db.session import get_db
from fastapi.responses import FileResponse
from app.models.fatura import Fatura
import os

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

@router.get("/{siparis_id}/fatura", response_class=FileResponse)
def faturayi_indir(
    siparis_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user),
):
    """
    Belirtilen siparişe ait faturayı indirir.
    Kullanıcı sadece kendi siparişinin faturasını indirebilir.
    """
    # Önce siparişin varlığını ve bu kullanıcıya ait olduğunu kontrol et
    siparis = db.query(models.Siparis).filter(
        models.Siparis.id == siparis_id,
        models.Siparis.kullanici_id == current_user.id
    ).first()

    if not siparis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sipariş bulunamadı veya bu siparişe erişim yetkiniz yok.")

    # Siparişe ait faturayı bul
    fatura = db.query(Fatura).filter(Fatura.siparis_id == siparis_id).first()

    if not fatura:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bu siparişe ait bir fatura bulunamadı.")

    fatura_yolu = fatura.fatura_yolu
    if not os.path.exists(fatura_yolu):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Fatura dosyası sunucuda bulunamadı. Lütfen yönetici ile iletişime geçin.")

    # FastAPI'nin FileResponse'u kullanarak dosyayı döndür
    return FileResponse(
        path=fatura_yolu,
        filename=os.path.basename(fatura_yolu), # Tarayıcıda görünecek dosya adı
        media_type='application/pdf'
    )