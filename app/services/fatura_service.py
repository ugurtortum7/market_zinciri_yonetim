# app/services/fatura_service.py
from sqlalchemy.orm import Session
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from decimal import Decimal
from io import BytesIO
from app import models
from app.core.logging_config import get_logger

log = get_logger(__name__)

def generate_invoice_pdf_in_memory(siparis: models.Siparis) -> BytesIO:
    log.info(f"Sipariş {siparis.id} için fatura hafızada oluşturuluyor...")
    try:
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        c.setFont("Helvetica-Bold", 18)
        c.drawString(inch, height - inch, "FATURA")

        c.setFont("Helvetica", 12)
        c.drawString(inch, height - 1.5 * inch, f"Musteri: {siparis.kullanici.kullanici_adi}")
        c.drawString(inch, height - 1.7 * inch, f"Siparis ID: {siparis.id}")
        c.drawString(inch, height - 1.9 * inch, f"Siparis Tarihi: {siparis.siparis_tarihi.strftime('%d-%m-%Y %H:%M')}")
        
        # Ürünler Başlıkları
        c.setFont("Helvetica-Bold", 12)
        y_pos = height - 2.5 * inch
        c.drawString(inch, y_pos, "Urun Adi")
        c.drawString(inch * 4, y_pos, "Miktar")
        c.drawString(inch * 5, y_pos, "Birim Fiyat")
        c.drawString(inch * 6.5, y_pos, "Toplam")
        c.line(inch, y_pos - 0.1 * inch, width - inch, y_pos - 0.1 * inch)

        c.setFont("Helvetica", 10)
        y_pos -= 0.3 * inch
        for detay in siparis.detaylar:
            if not detay.urun: continue
            urun_adi = detay.urun.urun_adi
            miktar = str(detay.miktar)
            birim_fiyat = f"{Decimal(detay.urun_fiyati):.2f} TL"
            toplam_fiyat = f"{(detay.miktar * Decimal(detay.urun_fiyati)):.2f} TL"
            c.drawString(inch, y_pos, urun_adi)
            c.drawString(inch * 4.2, y_pos, miktar)
            c.drawString(inch * 5.2, y_pos, birim_fiyat)
            c.drawString(inch * 6.7, y_pos, toplam_fiyat)
            y_pos -= 0.3 * inch

        c.line(inch, y_pos, width - inch, y_pos)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(inch * 5, y_pos - 0.5 * inch, "Genel Toplam:")
        c.drawString(inch * 6.5, y_pos - 0.5 * inch, f"{Decimal(siparis.toplam_tutar):.2f} TL")
        
        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer
    except Exception as e:
        log.error(f"Hafizada PDF olusturma hatasi (Siparis ID: {siparis.id}): {e}", exc_info=True)
        raise e # Hatayı yukarı fırlat ki fark edilsin