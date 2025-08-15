from app.db.session import SessionLocal
from app.services import sevkiyat_service
from app.schemas.sevkiyat import SevkiyatCreate, SevkiyatUrunCreate
from app.core.logging_config import get_logger
from app.models.lokasyon import Lokasyon
from app.models.urun import Urun

log = get_logger("zamanlanmis_gorev")

SEVKIYAT_PAKETI = {
    "SUT-TY-1L": 50,  
    "SABUN-SV-500mL": 10,   
    "EKMEK-250GR": 100       
}

def gunluk_standart_sevkiyat():
    """
    Tüm süpermarketlere, önceden tanımlanmış standart ürün paketini sevk eder.
    """
    log.info("--- Günlük Standart Sevkiyat Görevi Başladı ---")
    
    db = SessionLocal()
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
                    urunler_listesi.append(
                        SevkiyatUrunCreate(urun_id=urun.id, miktar=miktar)
                    )
                else:
                    log.error(f"'{sku}' SKU'lu ürün veritabanında bulunamadı! Bu ürün sevkiyattan atlanacak.")
            
            if not urunler_listesi:
                log.warning(f"'{market.ad}' için gönderilecek geçerli ürün bulunamadı. Bu market için sevkiyat oluşturulmuyor.")
                continue

            sevkiyat_data = SevkiyatCreate(
                hedef_lokasyon_id=market.id,
                urunler=urunler_listesi
            )

            try:
                sevkiyat_service.create_sevkiyat(db=db, sevkiyat_data=sevkiyat_data)
                log.info(f"'{market.ad}' için sevkiyat başarıyla oluşturuldu.")
            except Exception as sevkiyat_hatasi:
                log.error(f"'{market.ad}' için sevkiyat oluşturulurken bir hata oluştu: {sevkiyat_hatasi}")


    except Exception as e:
        log.critical(f"Görev sırasında beklenmedik bir genel hata oluştu: {e}")
    finally:
        db.close()
        log.info("--- Günlük Standart Sevkiyat Görevi Bitti ---")


if __name__ == "__main__":
    gunluk_standart_sevkiyat()