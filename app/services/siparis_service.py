# app/services/siparis_service.py
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from decimal import Decimal
from typing import List
from app import models
from app.models.user import User
from app.models.siparis import Siparis, SiparisDetay
from app.models.sepet import SepetUrunu
from app.schemas.siparis_schema import SiparisCreate
from . import stok_service

def get_kullanici_siparisleri(db: Session, kullanici_id: int) -> List[Siparis]:
    return db.query(models.Siparis).options(
        joinedload(models.Siparis.detaylar).joinedload(models.SiparisDetay.urun),
        joinedload(models.Siparis.kullanici) # Kullanıcı bilgisini de yükle
    ).filter(models.Siparis.kullanici_id == kullanici_id).order_by(models.Siparis.siparis_tarihi.desc()).all()

def create_order_from_cart(db: Session, kullanici: User, siparis_data: SiparisCreate) -> Siparis:
    sepet = db.query(models.Sepet).options(
        joinedload(models.Sepet.urunler).joinedload(SepetUrunu.urun)
    ).filter(models.Sepet.kullanici_id == kullanici.id).first()
    if not sepet or not sepet.urunler:
        raise HTTPException(status_code=400, detail="Sepetinizde ürün olmalıdır.")

    # ... (Stok kontrolü ve toplam tutar hesaplama mantığı aynı)
    toplam_tutar = sum(Decimal(str(item.urun.fiyat)) * item.miktar for item in sepet.urunler)
    market_lokasyonu = db.query(models.Lokasyon).filter(models.Lokasyon.ad == "TORMAR").first()
    # ... (Stok kontrol döngüsü)
    
    yeni_siparis = Siparis(
        kullanici_id=kullanici.id,
        teslimat_adresi=siparis_data.teslimat_adresi,
        toplam_tutar=toplam_tutar
    )
    db.add(yeni_siparis)
    db.flush() # Yeni siparişin ID'sini almak için

    for item in sepet.urunler:
        # Stok düşme
        stok_service.update_stok_miktari(db, market_lokasyonu.id, item.urun_id, -item.miktar)
        # Sipariş detayı
        siparis_detayi = SiparisDetay(siparis_id=yeni_siparis.id, urun_id=item.urun_id, miktar=item.miktar, urun_fiyati=Decimal(str(item.urun.fiyat)))
        db.add(siparis_detayi)
        
    db.query(SepetUrunu).filter(SepetUrunu.sepet_id == sepet.id).delete(synchronize_session=False)
    db.commit()
    db.refresh(yeni_siparis)
    return yeni_siparis