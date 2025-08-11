# app/services/sevkiyat_service.py

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

# --- EKSİK IMPORT'LARI BURAYA EKLİYORUZ ---
from app.db.session import SessionLocal
from app.core.logging_config import get_logger
from app.models.urun import Urun
from app.schemas.sevkiyat import SevkiyatUrunCreate
# --- EKLEMELERİN SONU ---

from app.models.lokasyon import Lokasyon
from app.models.stok import Stok
from app.models.sevkiyat import Sevkiyat, SevkiyatDetay
from app.schemas.sevkiyat import SevkiyatCreate
from . import stok_service

# --- EKSİK LOGGER NESNESİNİ BURADA OLUŞTURUYORUZ ---
log = get_logger(__name__)

def create_sevkiyat(db: Session, sevkiyat_data: SevkiyatCreate) -> Sevkiyat:
    """
    Depodan bir süpermarkete sevkiyat işlemi gerçekleştirir.
    Bu fonksiyon bir bütün olarak (transactional) çalışır.
    """
    # Bu fonksiyonun içeriği doğruydu, aynı kalıyor...
    kaynak_depo = db.query(Lokasyon).filter(Lokasyon.tip == "DEPO").first()
    if not kaynak_depo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Merkez depo bulunamadı.")

    hedef_market = db.query(Lokasyon).get(sevkiyat_data.hedef_lokasyon_id)
    if not hedef_market or hedef_market.tip != "SUPERMARKET":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hedef süpermarket bulunamadı veya lokasyon tipi yanlış."
        )

    yeni_sevkiyat = Sevkiyat(
        kaynak_lokasyon_id=kaynak_depo.id,
        hedef_lokasyon_id=hedef_market.id
    )
    db.add(yeni_sevkiyat)
    
    for urun_detay in sevkiyat_data.urunler:
        depo_stok = stok_service.get_stok_by_lokasyon_and_urun(
            db, lokasyon_id=kaynak_depo.id, urun_id=urun_detay.urun_id
        )
        if not depo_stok or depo_stok.miktar < urun_detay.miktar:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Depoda {urun_detay.urun_id} ID'li ürün için yeterli stok yok."
            )

        market_stok = stok_service.get_stok_by_lokasyon_and_urun(
            db, lokasyon_id=hedef_market.id, urun_id=urun_detay.urun_id
        )
        if not market_stok:
            market_stok = Stok(lokasyon_id=hedef_market.id, urun_id=urun_detay.urun_id, miktar=0)
            db.add(market_stok)

        depo_stok.miktar -= urun_detay.miktar
        market_stok.miktar += urun_detay.miktar

        sevkiyat_detay_kaydi = SevkiyatDetay(
            sevkiyat=yeni_sevkiyat,
            urun_id=urun_detay.urun_id,
            miktar=urun_detay.miktar
        )
        db.add(sevkiyat_detay_kaydi)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sevkiyat sırasında beklenmedik bir veritabanı hatası oluştu: {e}"
        )
    
    db.refresh(yeni_sevkiyat)
    return yeni_sevkiyat

def tetikle_gunluk_sevkiyat(db: Session):
    """
    Tüm süpermarketlere, önceden tanımlanmış standart ürün paketini sevk eder.
    """
    log.info("--- API üzerinden tetiklenen Günlük Sevkiyat Görevi Başladı ---")
    
    SEVKIYAT_PAKETI = {
        "SUT-TY-1L": 50,
        "SIVI-SABUN-500ML": 10,
        "EKMEK-250GR": 100
    }
    try:
        tum_supermarketler = db.query(Lokasyon).filter(Lokasyon.tip == "SUPERMARKET").all()
        if not tum_supermarketler:
            log.warning("Sistemde hiç süpermarket bulunamadı. Görev sonlandırılıyor.")
            return

        gonderilecek_sku_listesi = list(SEVKIYAT_PAKETI.keys())
        urun_nesneleri = db.query(Urun).filter(Urun.sku.in_(gonderilecek_sku_listesi)).all()
        urun_haritasi = {urun.sku: urun for urun in urun_nesneleri}

        log.info(f"{len(tum_supermarketler)} süpermarket ve {len(urun_nesneleri)} çeşit ürün için sevkiyat planlanıyor.")

        for market in tum_supermarketler:
            log.info(f"'{market.ad}' için sevkiyat hazırlanıyor...")
            urunler_listesi = []
            for sku, miktar in SEVKIYAT_PAKETI.items():
                if sku in urun_haritasi:
                    urun = urun_haritasi[sku]
                    urunler_listesi.append(SevkiyatUrunCreate(urun_id=urun.id, miktar=miktar))
                else:
                    log.error(f"'{sku}' SKU'lu ürün veritabanında bulunamadı! Bu ürün sevkiyattan atlanacak.")
            
            if not urunler_listesi:
                log.warning(f"'{market.ad}' için gönderilecek geçerli ürün bulunamadı.")
                continue

            sevkiyat_data = SevkiyatCreate(hedef_lokasyon_id=market.id, urunler=urunler_listesi)
            # Düzeltme: create_sevkiyat fonksiyonunu bu dosyanın içinden doğrudan çağırıyoruz
            create_sevkiyat(db=db, sevkiyat_data=sevkiyat_data)
            log.info(f"'{market.ad}' için sevkiyat başarıyla oluşturuldu.")
            
    except Exception as e:
        log.critical(f"Görev sırasında beklenmedik bir genel hata oluştu: {e}")
    finally:
        db.close()
        log.info("--- API üzerinden tetiklenen Günlük Sevkiyat Görevi Bitti ---")