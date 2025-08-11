from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from decimal import Decimal

from app.models.user import User
from app.models.satis import Satis, SatisDetay
from app.schemas.satis import SatisCreate
from . import stok_service

def create_satis(
    db: Session, 
    satis_data: SatisCreate, 
    kasiyer: User,
):
    toplam_tutar = Decimal(0)
    yeni_satis = Satis(
        lokasyon_id=kasiyer.lokasyon_id,
        kasiyer_id=kasiyer.id,
        toplam_tutar=0
    )
    db.add(yeni_satis)

    for urun_detay in satis_data.urunler:
        market_stok = stok_service.get_stok_by_lokasyon_and_urun(
            db, lokasyon_id=kasiyer.lokasyon_id, urun_id=urun_detay.urun_id
        )
        if not market_stok or market_stok.miktar < urun_detay.miktar:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Markette {urun_detay.urun_id} ID'li ürün için yeterli stok yok."
            )
        
        market_stok.miktar -= urun_detay.miktar
        
        satis_detay_kaydi = SatisDetay(
            satis=yeni_satis,
            urun_id=urun_detay.urun_id,
            miktar=urun_detay.miktar,
            satis_fiyati=Decimal(urun_detay.satis_fiyati)
        )
        db.add(satis_detay_kaydi)
        toplam_tutar += Decimal(urun_detay.satis_fiyati) * urun_detay.miktar

    yeni_satis.toplam_tutar = toplam_tutar

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Satış sırasında beklenmedik bir veritabanı hatası oluştu: {e}"
        )
    
    return {"message": "Satış başarıyla tamamlandı.", "satis_id": yeni_satis.id}