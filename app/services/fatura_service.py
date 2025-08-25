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

# Faturaların kaydedileceği klasörü belirliyoruz.
FATURA_KLASORU = "faturalar"

def generate_invoice_pdf(db: Session, siparis: models.Siparis):
    """
    Verilen sipariş için bir PDF faturası oluşturur, dosyayı kaydeder
    ve veritabanına Fatura kaydını ekler.
    """
    if not os.path.exists(FATURA_KLASORU):
        os.makedirs(FATURA_KLASORU)

    dosya_adi = f"fatura_siparis_{siparis.id}.pdf"
    dosya_yolu = os.path.join(FATURA_KLASORU, dosya_adi)

    try:
        c = canvas.Canvas(dosya_yolu, pagesize=letter)
        width, height = letter

        # Türkçe karakter desteği için font ayarı
        try:
            pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
            FONT_NORMAL = "DejaVuSans"
            FONT_BOLD = "DejaVuSans-Bold"
            # Kalın fontu da kaydetmeye çalış, yoksa normali kullan
            try:
                pdfmetrics.registerFont(TTFont(FONT_BOLD, 'DejaVuSans-Bold.ttf'))
            except:
                FONT_BOLD = "DejaVuSans" 
        except:
            log.warning("DejaVuSans fontu bulunamadı. Standart font kullanılıyor.")
            FONT_NORMAL = "Helvetica"
            FONT_BOLD = "Helvetica-Bold"

        # ---- Fatura Başlığı ----
        c.setFont(FONT_BOLD, 18)
        c.drawString(inch, height - inch, "FATURA")

        # ---- Müşteri ve Sipariş Bilgileri ----
        c.setFont(FONT_NORMAL, 12)
        # ===== DÜZELTME 1: Doğru kullanıcı adı alanı kullanıldı =====
        c.drawString(inch, height - 1.5 * inch, f"Müşteri: {siparis.kullanici.kullanici_adi}")
        c.drawString(inch, height - 1.7 * inch, f"Sipariş ID: {siparis.id}")
        c.drawString(inch, height - 1.9 * inch, f"Sipariş Tarihi: {siparis.siparis_tarihi.strftime('%d-%m-%Y %H:%M')}")
        c.drawString(inch, height - 2.1 * inch, f"Teslimat Adresi: {siparis.teslimat_adresi}")

        # ---- Ürünler Tablosu Başlıkları ----
        c.setFont(FONT_BOLD, 12)
        y_pos = height - 3 * inch
        c.drawString(inch, y_pos, "Ürün Adı")
        c.drawString(inch * 4, y_pos, "Miktar")
        c.drawString(inch * 5, y_pos, "Birim Fiyat")
        c.drawString(inch * 6.5, y_pos, "Toplam")
        c.line(inch, y_pos - 0.1 * inch, width - inch, y_pos - 0.1 * inch)

        # ---- Sipariş Detaylarını Yazdır ----
        c.setFont(FONT_NORMAL, 10)
        y_pos -= 0.3 * inch
        for detay in siparis.detaylar:
            # ===== DÜZELTME 2: Gerçek ürün adı (ilişkiden gelen) kullanılıyor =====
            urun_adi = detay.urun.urun_adi if detay.urun else "Bilinmeyen Ürün"
            miktar = str(detay.miktar)
            birim_fiyat = f"{Decimal(detay.urun_fiyati):.2f} TL"
            toplam_fiyat = f"{(detay.miktar * Decimal(detay.urun_fiyati)):.2f} TL"

            c.drawString(inch, y_pos, urun_adi)
            c.drawString(inch * 4.2, y_pos, miktar)
            c.drawString(inch * 5.2, y_pos, birim_fiyat)
            c.drawString(inch * 6.7, y_pos, toplam_fiyat)
            y_pos -= 0.3 * inch

        # ---- Genel Toplam ----
        c.line(inch, y_pos, width - inch, y_pos)
        c.setFont(FONT_BOLD, 14)
        c.drawString(inch * 5, y_pos - 0.5 * inch, "Genel Toplam:")
        c.drawString(inch * 6.5, y_pos - 0.5 * inch, f"{Decimal(siparis.toplam_tutar):.2f} TL")

        c.save()

        mevcut_fatura = db.query(models.Fatura).filter(models.Fatura.siparis_id == siparis.id).first()
        if mevcut_fatura:
            mevcut_fatura.fatura_yolu = dosya_yolu
        else:
            yeni_fatura = models.Fatura(siparis_id=siparis.id, fatura_yolu=dosya_yolu)
            db.add(yeni_fatura)
        
        db.commit()
        log.info(f"Sipariş {siparis.id} için fatura oluşturuldu: {dosya_yolu}")
        return True

    except Exception as e:
        db.rollback()
        log.error(f"Fatura oluşturma hatası (Sipariş ID: {siparis.id}): {e}")
        return None