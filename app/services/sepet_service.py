# app/services/sepet_service.py

from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime

from app.models.sepet import Sepet, SepetUrunu
from app.models.lokasyon import Lokasyon
from app.schemas.sepet_schema import SepetUrunuCreate
from . import stok_service

def get_veya_create_kullanici_sepeti(db: Session, kullanici_id: int) -> Sepet:
    """
    Bir kullanıcının sepetini, içindeki ürünler ve ürün detaylarıyla birlikte getirir.
    Eğer sepeti yoksa, otomatik olarak yeni ve boş bir sepet oluşturur.
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
        # Yeni oluşturulan sepeti, ilişkileriyle birlikte tekrar sorgulayalım ki yapı tutarlı olsun
        sepet = (
            db.query(Sepet)
            .options(joinedload(Sepet.urunler).joinedload(SepetUrunu.urun))
            .filter(Sepet.kullanici_id == kullanici_id)
            .first()
        )

    return sepet

def sepete_urun_ekle(db: Session, kullanici_id: int, urun_data: SepetUrunuCreate) -> Sepet:
    """
    Kullanıcının sepetine bir ürün ekler.
    - Eğer ürün sepette zaten varsa, miktarını artırır.
    - Eklemeden önce merkez depo stoğunu kontrol eder.
    """
    # 1. Kullanıcının sepetini al (yoksa oluştur).
    sepet = get_veya_create_kullanici_sepeti(db, kullanici_id=kullanici_id)
    
    # 2. Merkez depo stoğunu kontrol et.
    merkez_depo = db.query(Lokasyon).filter(Lokasyon.tip == "DEPO").first()
    if not merkez_depo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Merkez depo bulunamadı.")
        
    depo_stok = stok_service.get_stok_by_lokasyon_and_urun(db, lokasyon_id=merkez_depo.id, urun_id=urun_data.urun_id)
    
    # 3. Sepetteki mevcut ürünü bul (varsa).
    sepetteki_urun = db.query(SepetUrunu).filter(
        SepetUrunu.sepet_id == sepet.id,
        SepetUrunu.urun_id == urun_data.urun_id
    ).first()
    
    mevcut_miktar = sepetteki_urun.miktar if sepetteki_urun else 0
    istenen_toplam_miktar = mevcut_miktar + urun_data.miktar
    
    if not depo_stok or depo_stok.miktar < istenen_toplam_miktar:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Depoda ürün için yeterli stok yok. Mevcut stok: {depo_stok.miktar if depo_stok else 0}"
        )
        
    # 4. Ürünü sepete ekle veya miktarını güncelle.
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
    
    return sepet

def sepet_urun_miktarini_guncelle(db: Session, kullanici_id: int, urun_id: int, yeni_miktar: int) -> Sepet:
    """
    Sepetteki bir ürünün miktarını günceller.
    Eğer miktar 0 veya daha aza indirilirse, ürünü sepetten siler.
    """
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
    return sepet

def sepeti_temizle(db: Session, kullanici_id: int):
    """
    Bir kullanıcının sepetindeki tüm ürünleri siler.
    """
    sepet = db.query(Sepet).filter(Sepet.kullanici_id == kullanici_id).first()
    if sepet:
        db.query(SepetUrunu).filter(SepetUrunu.sepet_id == sepet.id).delete()
        sepet.guncellenme_tarihi = datetime.now()
        db.commit()
    return {"message": "Sepet başarıyla temizlendi."}