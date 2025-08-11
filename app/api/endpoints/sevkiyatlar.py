from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import schemas, models, services
from app.api import dependencies
from app.db.session import get_db

router = APIRouter()

@router.post("/", response_model=schemas.Sevkiyat)
def create_sevkiyat(
    sevkiyat: schemas.SevkiyatCreate,
    db: Session = Depends(get_db),
    current_manager: models.User = Depends(dependencies.get_current_manager_user)
):
    """
    Depodan bir süpermarkete yeni bir sevkiyat oluşturur.
    Bu işlem stokları otomatik olarak günceller.
    Sadece Yöneticiler erişebilir.
    """
    yeni_sevkiyat_orm = services.sevkiyat_service.create_sevkiyat(db=db, sevkiyat_data=sevkiyat)
    
    detaylar_listesi = [
        schemas.SevkiyatUrun(
            urun_adi=detay.urun.urun_adi,
            sku=detay.urun.sku,
            miktar=detay.miktar
        ) for detay in yeni_sevkiyat_orm.sevkiyat_detaylari
    ]

    return schemas.Sevkiyat(
        id=yeni_sevkiyat_orm.id,
        kaynak_lokasyon_ad=yeni_sevkiyat_orm.kaynak_lokasyon.ad,
        hedef_lokasyon_ad=yeni_sevkiyat_orm.hedef_lokasyon.ad,
        sevkiyat_tarihi=str(yeni_sevkiyat_orm.sevkiyat_tarihi),
        detaylar=detaylar_listesi
    )