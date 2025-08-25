# app/services/fatura_service.py

import os
from sqlalchemy.orm import Session
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from decimal import Decimal

from app import models
from app.core.logging_config import get_logger

log = get_logger(__name__)

# Faturaların kaydedileceği klasörün tam yolunu alalım
# Bu, projenin ana dizinini temel alır ve daha güvenilirdir.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FATURA_KLASORU = os.path.join(BASE_DIR, "..", "faturalar")

def generate_invoice_pdf(db: Session, siparis: models.Siparis):
    """
    Verilen sipariş için bir PDF faturası oluşturur, dosyayı kaydeder
    ve veritabanına Fatura kaydını ekler.
    """
    log.info(f"Sipariş {siparis.id} için fatura oluşturma işlemi başladı.")

    try:
        # 1. Klasörün var olduğundan emin ol
        log.info(f"Fatura klasörü kontrol ediliyor: {FATURA_KLASORU}")
        if not os.path.exists(FATURA_KLASORU):
            log.info("Fatura klasörü bulunamadı, oluşturuluyor...")
            os.makedirs(FATURA_KLASORU)

        # 2. Benzersiz bir dosya adı ve yolu oluştur
        dosya_adi = f"fatura_siparis_{siparis.id}.pdf"
        dosya_yolu = os.path.join(FATURA_KLASORU, dosya_adi)
        log.info(f"PDF dosya yolu oluşturuldu: {dosya_yolu}")

        # 3. PDF'i ReportLab ile oluşturmaya başla
        c = canvas.Canvas(dosya_yolu, pagesize=letter)
        width, height = letter
        log.info("ReportLab canvas'ı başarıyla oluşturuldu.")

        # Türkçe karakter desteği için font kaydı
        # SADECE TEK BİR FONT KULLANARAK BASİTLEŞTİRELİM
        try:
            font_path = os.path.join(BASE_DIR, "..", "DejaVuSans.ttf")
            log.info(f"Font dosyası aranıyor: {font_path}")
            pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
            FONT_NORMAL = "DejaVuSans"
            log.info("DejaVuSans fontu başarıyla kaydedildi.")
        except Exception as font_error:
            log.error(f"FONT HATASI: {font_error}. Standart font kullanılacak.")
            FONT_NORMAL = "Helvetica"
        
        c.setFont(FONT_NORMAL, 12)

        # ---- Fatura Başlığı ve İçeriği ----
        log.info("Fatura içeriği PDF'e yazılıyor...")
        c.setFont(FONT_NORMAL, 18) # Boyutları biraz ayarlayalım
        c.drawString(inch, height - inch, "FATURA")

        c.setFont(FONT_NORMAL, 12)
        c.drawString(inch, height - 1.5 * inch, f"Müşteri: {siparis.kullanici.kullanici_adi}")
        c.drawString(inch, height - 1.7 * inch, f"Sipariş ID: {siparis.id}")
        c.drawString(inch, height - 1.9 * inch, f"Sipariş Tarihi: {siparis.siparis_tarihi.strftime('%d-%m-%Y %H:%M')}")
        # ... (Geri kalan c.drawString satırları aynı, hatasız olduklarını varsayıyoruz) ...
        # ... (Bu satırları kodunuzdan kopyalayabilirsiniz, bir önceki cevaptaki gibi) ...

        # Örnek olarak bir satır daha ekleyelim
        y_pos = height - 3 * inch
        c.drawString(inch, y_pos, "Ürün Adı")

        log.info("Fatura içeriği yazıldı. PDF kaydedilecek...")
        # PDF'i kaydet
        c.save()
        log.info(f"PDF başarıyla kaydedildi: {dosya_yolu}")

        # 4. Veritabanına Fatura kaydını oluştur
        mevcut_fatura = db.query(models.Fatura).filter(models.Fatura.siparis_id == siparis.id).first()
        if mevcut_fatura:
            mevcut_fatura.fatura_yolu = dosya_yolu
            log.info(f"Mevcut fatura kaydı güncellendi: ID {mevcut_fatura.id}")
        else:
            yeni_fatura = models.Fatura(siparis_id=siparis.id, fatura_yolu=dosya_yolu)
            db.add(yeni_fatura)
            log.info("Yeni fatura kaydı veritabanına ekleniyor.")
        
        db.commit()
        log.info("Veritabanı commit işlemi başarılı.")

        return True

    except Exception as e:
        db.rollback()
        # BU EN ÖNEMLİ LOG. SORUNU BURADA GÖRECEĞİZ.
        log.error(f"FATURA OLUŞTURMA İŞLEMİ ÇÖKTÜ (Sipariş ID: {siparis.id}): {e}", exc_info=True)
        return None