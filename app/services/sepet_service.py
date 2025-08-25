# app/services/sepet_service.py

from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from typing import Optional
from datetime import datetime

from app.models.sepet import Sepet, SepetUrunu
from app.models.lokasyon import Lokasyon
from app.schemas.sepet_schema import SepetUrunuCreate
from . import stok_service

def get_veya_create_kullanici_sepeti(db: Session, kullanici_id: int) -> Sepet:
    """
    Kullanıcının sepetini, ilişkili tüm verilerle birlikte (urunler ve urun detayları)
    güvenli bir şekilde getirir. Sepet yoksa oluşturur.
    Bu versiyon, boş sepetlerde çökme sorununu çözer.
    """
    sepet = (
        db.query(Sepet)
        .options(joinedload(Sepet.urunler).joinedload(SepetUrunu.urun))
        .filter(Sepet.kullanici_id == kullanici_id)
        .first()
    )
    
    if not sepet:
        yeni_sepet = Sepet(kullanici_id=kullanici_id)
        db.add(yeni_sepet)
        db.commit()
        db.refresh(yeni_sepet)
        # Yeni oluşturulan sepeti, ilişkileriyle birlikte tekrar sorguluyoruz ki yapı tutarlı olsun
        sepet = (
            db.query(Sepet)
            .options(joinedload(Sepet.urunler).joinedload(SepetUrunu.urun))
            .filter(Sepet.kullanici_id == kullanici_id)
            .first()
        )

    return sepet

def sepete_urun_ekle(db: Session, kullanici_id: int, urun_data: SepetUrunuCreate) -> Sepet:
    sepet = get_veya_create_kullanici_sepeti(db, kullanici_id=kullanici_id)
    
    market_lokasyonu = db.query(Lokasyon).filter(Lokasyon.ad == "TORMAR").first()
    if not market_lokasyonu:
        raise HTTPException(status_code=500, detail="TORMAR market lokasyonu bulunamadı.")
        
    market_stok = stok_service.get_stok_by_lokasyon_and_urun(db, lokasyon_id=market_lokasyonu.id, urun_id=urun_data.urun_id)
    
    sepetteki_urun = db.query(SepetUrunu).filter(
        SepetUrunu.sepet_id == sepet.id,
        SepetUrunu.urun_id == urun_data.urun_id
    ).first()
    
    mevcut_miktar = sepetteki_urun.miktar if sepetteki_urun else 0
    istenen_toplam_miktar = mevcut_miktar + urun_data.miktar
    
    if not market_stok or market_stok.miktar < istenen_toplam_miktar:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stok yetersiz. Mevcut stok: {market_stok.miktar if market_stok else 0}"
        )
        
    if sepetteki_urun:
        sepetteki_urun.miktar += urun_data.miktar
    else:
        yeni_sepet_urunu = SepetUrunu(
            sepet_id=sepet.id,
            urun_id=urun_data.urun_id,
            miktar=urun_data.miktar
        )
        db.add(yeni_sepet_urunu)
        
    sepet.guncellenme_tarihi = datetime.now()
    db.commit()
    db.refresh(sepet)
    return get_veya_create_kullanici_sepeti(db, kullanici_id=kullanici_id)

def sepet_urun_miktarini_guncelle(db: Session, kullanici_id: int, urun_id: int, yeni_miktar: int) -> Sepet:
    sepet = get_veya_create_kullanici_sepeti(db, kullanici_id)
    sepetteki_urun = db.query(SepetUrunu).filter(
        SepetUrunu.sepet_id == sepet.id,
        SepetUrunu.urun_id == urun_id
    ).first()

    if not sepetteki_urun:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ürün sepette bulunamadı.")
    
    if yeni_miktar <= 0:
        db.delete(sepetteki_urun)
    else:
        sepetteki_urun.miktar = yeni_miktar
        
    sepet.guncellenme_tarihi = datetime.now()
    db.commit()
    db.refresh(sepet)
    return get_veya_create_kullanici_sepeti(db, kullanici_id=kullanici_id)

def sepeti_temizle(db: Session, kullanici_id: int):
    sepet = db.query(Sepet).filter(Sepet.kullanici_id == kullanici_id).first()
    if sepet:
        db.query(SepetUrunu).filter(SepetUrunu.sepet_id == sepet.id).delete()
        sepet.guncellenme_tarihi = datetime.now()
        db.commit()
    return get_veya_create_kullanici_sepeti(db, kullanici_id=kullanici_id)