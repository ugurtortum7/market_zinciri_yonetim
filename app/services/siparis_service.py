# app/services/siparis_service.py

from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from decimal import Decimal
from typing import List # List'i import etmeyi unutmayın
from app import models
from app.models.user import User
from app.models.siparis import Siparis, SiparisDetay
from app.schemas.siparis_schema import SiparisCreate
from . import sepet_service, stok_service, fatura_service
from app.core.logging_config import get_logger

log = get_logger(__name__)

# ===== YENİ EKLENEN VE DÜZELTİLEN FONKSİYON =====
def get_kullanici_siparisleri(db: Session, kullanici_id: int) -> List[Siparis]:
    """
    Kullanıcının geçmiş siparişlerini, detayları ve ürün bilgileriyle birlikte getirir.
    Bu, frontend'in çökmesine neden olan sorunu çözer.
    """
    return (
        db.query(models.Siparis)
        .options(
            joinedload(models.Siparis.detaylar)
            .joinedload(models.SiparisDetay.urun)
        )
        .filter(models.Siparis.kullanici_id == kullanici_id)
        .order_by(models.Siparis.siparis_tarihi.desc())
        .all()
    )
# ===============================================

def create_order_from_cart(db: Session, kullanici: User, siparis_data: SiparisCreate) -> Siparis:
    """
    Kullanıcının mevcut sepetinden bir sipariş oluşturur.
    """
    sepet = db.query(models.Sepet).options(
        joinedload(models.Sepet.urunler).joinedload(models.SepetUrunu.urun)
    ).filter(models.Sepet.kullanici_id == kullanici.id).first()

    if not sepet or not sepet.urunler:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sipariş oluşturmak için sepetinizde ürün olmalıdır.")

    toplam_tutar = Decimal(0)
    merkez_depo = db.query(models.Lokasyon).filter(models.Lokasyon.tip == "DEPO").first()
    if not merkez_depo:
        raise HTTPException(status_code=500, detail="Merkez depo yapılandırılmamış.")

    for item in sepet.urunler:
        # ===== DÜZELTİLEN KISIM: Gerçek ürün fiyatını kullanıyoruz =====
        if not item.urun or item.urun.fiyat is None:
             raise HTTPException(status_code=500, detail=f"'{item.urun.urun_adi if item.urun else 'Bilinmeyen'}' ürününün fiyat bilgisi bulunamadı.")
        
        fiyat = Decimal(str(item.urun.fiyat)) # Fiyatı Decimal'e çeviriyoruz
        toplam_tutar += item.miktar * fiyat
        # ========================================================
        
        depo_stok = stok_service.get_stok_by_lokasyon_and_urun(db, lokasyon_id=merkez_depo.id, urun_id=item.urun_id)
        if not depo_stok or depo_stok.miktar < item.miktar:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"'{item.urun.urun_adi}' için stok yetersiz. Sipariş oluşturulamadı."
            )

    try:
        yeni_siparis = Siparis(
            kullanici_id=kullanici.id,
            teslimat_adresi=siparis_data.teslimat_adresi,
            toplam_tutar=toplam_tutar
        )
        db.add(yeni_siparis)

        for item in sepet.urunler:
            depo_stok = stok_service.get_stok_by_lokasyon_and_urun(db, lokasyon_id=merkez_depo.id, urun_id=item.urun_id)
            depo_stok.miktar -= item.miktar
            
            siparis_detayi = SiparisDetay(
                siparis=yeni_siparis,
                urun_id=item.urun_id,
                miktar=item.miktar,
                # ===== DÜZELTİLEN KISIM: Gerçek ürün fiyatını kaydediyoruz =====
                urun_fiyati=Decimal(str(item.urun.fiyat))
                # ========================================================
            )
            db.add(siparis_detayi)
            
        db.query(models.SepetUrunu).filter(models.SepetUrunu.sepet_id == sepet.id).delete(synchronize_session=False)

        db.commit()
        db.refresh(yeni_siparis)

        try:
            siparis_for_invoice = db.query(Siparis).options(
                joinedload(Siparis.kullanici),
                joinedload(Siparis.detaylar).joinedload(SiparisDetay.urun) # Ürünleri de yükle
            ).filter(Siparis.id == yeni_siparis.id).one()
            fatura_service.generate_invoice_pdf(db=db, siparis=siparis_for_invoice)
        except Exception as invoice_error:
            log.error(f"Sipariş {yeni_siparis.id} oluşturuldu ancak fatura hatası: {invoice_error}")

        return yeni_siparis

    except Exception as e:
        db.rollback()
        log.error(f"Sipariş oluşturma sırasında hata: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Sipariş oluşturulurken beklenmedik bir hata oluştu.")