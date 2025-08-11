# app/services/siparis_service.py

from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from decimal import Decimal
from app import models
from app.models.user import User
from app.models.siparis import Siparis, SiparisDetay
from app.schemas.siparis_schema import SiparisCreate
from . import sepet_service, stok_service
from app.core.logging_config import get_logger
log = get_logger(__name__)

def create_order_from_cart(db: Session, kullanici: User, siparis_data: SiparisCreate) -> Siparis:
    """
    Kullanıcının mevcut sepetinden bir sipariş oluşturur.
    - Stokları son bir kez kontrol eder ve düşürür.
    - Sepeti temizler.
    - Tüm bu işlemleri tek bir transaction içinde yapar.
    """
    # 1. Kullanıcının sepetini ve içindeki ürünleri al.
    sepet = db.query(models.Sepet).options(
        joinedload(models.Sepet.urunler).joinedload(models.SepetUrunu.urun)
    ).filter(models.Sepet.kullanici_id == kullanici.id).first()

    if not sepet or not sepet.urunler:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sipariş oluşturmak için sepetinizde ürün olmalıdır.")

    # 2. Toplam tutarı hesapla ve stokları son kez kontrol et.
    toplam_tutar = Decimal(0)
    merkez_depo = db.query(models.Lokasyon).filter(models.Lokasyon.tip == "DEPO").first()
    if not merkez_depo:
        raise HTTPException(status_code=500, detail="Merkez depo yapılandırılmamış.")

    for item in sepet.urunler:
        # Gerçek ürün fiyatını buradan almalıyız (gerçek projede Urun modelinde fiyat olurdu)
        # Şimdilik temsili bir fiyat varsayalım veya şemadan alalım. 
        # Bizim urun modelimizde fiyat yok, o yüzden temsili 1.0 yazalım.
        # Gerçek bir projede bu satir `item.urun.fiyat` gibi olurdu.
        fiyat = Decimal("1.0") 
        toplam_tutar += item.miktar * fiyat
        
        # Stokları son kez kontrol et
        depo_stok = stok_service.get_stok_by_lokasyon_and_urun(db, lokasyon_id=merkez_depo.id, urun_id=item.urun_id)
        if not depo_stok or depo_stok.miktar < item.miktar:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"'{item.urun.urun_adi}' için stok yetersiz. Sipariş oluşturulamadı."
            )

    try:
        # 3. Sipariş ve Sipariş Detay kayıtlarını oluştur.
        yeni_siparis = Siparis(
            kullanici_id=kullanici.id,
            teslimat_adresi=siparis_data.teslimat_adresi,
            toplam_tutar=toplam_tutar
        )
        db.add(yeni_siparis)

        for item in sepet.urunler:
            # Depo stoğunu düşür.
            depo_stok = stok_service.get_stok_by_lokasyon_and_urun(db, lokasyon_id=merkez_depo.id, urun_id=item.urun_id)
            depo_stok.miktar -= item.miktar
            
            # Sipariş detayı oluştur.
            siparis_detayi = SiparisDetay(
                siparis=yeni_siparis,
                urun_id=item.urun_id,
                miktar=item.miktar,
                urun_fiyati=Decimal("1.0") # Yine temsili fiyat
            )
            db.add(siparis_detayi)
            
        # 4. Sepetteki ürünleri temizle.
        db.query(models.SepetUrunu).filter(models.SepetUrunu.sepet_id == sepet.id).delete(synchronize_session=False)

        db.commit()
        db.refresh(yeni_siparis)
        return yeni_siparis
    
    except Exception as e:
        db.rollback()
        log.error(f"Sipariş oluşturma sırasında hata: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Sipariş oluşturulurken beklenmedik bir hata oluştu.")

def get_kullanici_siparisleri(db: Session, kullanici_id: int):
    """
    Bir kullanıcının tüm geçmiş siparişlerini listeler.
    """
    return db.query(Siparis).filter(Siparis.kullanici_id == kullanici_id).order_by(Siparis.siparis_tarihi.desc()).all()