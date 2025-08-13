import os
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from app import models
from app.core.logging_config import get_logger

log = get_logger(__name__)

# Faturaların kaydedileceği klasörü belirliyoruz.
# Projenin ana dizininde "faturalar" adında bir klasör olmalı.
FATURA_KLASORU = "faturalar"

def generate_invoice_pdf(db: Session, siparis: models.Siparis):
    """
    Verilen sipariş için bir PDF faturası oluşturur, dosyayı kaydeder
    ve veritabanına Fatura kaydını ekler.
    """
    # 1. Klasörün var olduğundan emin ol
    if not os.path.exists(FATURA_KLASORU):
        os.makedirs(FATURA_KLASORU)

    # 2. Benzersiz bir dosya adı ve yolu oluştur
    dosya_adi = f"fatura_siparis_{siparis.id}.pdf"
    dosya_yolu = os.path.join(FATURA_KLASORU, dosya_adi)

    try:
        # 3. PDF'i ReportLab ile oluşturmaya başla
        c = canvas.Canvas(dosya_yolu, pagesize=letter)
        width, height = letter # Sayfa boyutları

        # ---- Fatura Başlığı ----
        c.setFont("Helvetica-Bold", 16)
        c.drawString(inch, height - inch, "FATURA")

        # ---- Müşteri ve Sipariş Bilgileri ----
        c.setFont("Helvetica", 12)
        c.drawString(inch, height - 1.5 * inch, f"Müşteri: {siparis.kullanici.ad} {siparis.kullanici.soyad}")
        c.drawString(inch, height - 1.7 * inch, f"Sipariş ID: {siparis.id}")
        c.drawString(inch, height - 1.9 * inch, f"Sipariş Tarihi: {siparis.siparis_tarihi.strftime('%d-%m-%Y %H:%M')}")
        c.drawString(inch, height - 2.1 * inch, f"Teslimat Adresi: {siparis.teslimat_adresi}")

        # ---- Ürünler Tablosu Başlıkları ----
        c.setFont("Helvetica-Bold", 12)
        y_pos = height - 3 * inch
        c.drawString(inch, y_pos, "Ürün Adı")
        c.drawString(inch * 4, y_pos, "Miktar")
        c.drawString(inch * 5, y_pos, "Birim Fiyat")
        c.drawString(inch * 6.5, y_pos, "Toplam")
        c.line(inch, y_pos - 0.1 * inch, width - inch, y_pos - 0.1 * inch)

        # ---- Sipariş Detaylarını Yazdır ----
        c.setFont("Helvetica", 10)
        y_pos -= 0.3 * inch
        for detay in siparis.detaylar:
            # Gerçek projede ürün adı detay.urun.urun_adi gibi olurdu.
            # Urun ilişkisini sorguya eklemek gerekir. Şimdilik ID yazalım.
            urun_adi = f"Ürün ID: {detay.urun_id}" 
            miktar = str(detay.miktar)
            birim_fiyat = f"{detay.urun_fiyati:.2f} TL"
            toplam_fiyat = f"{detay.miktar * detay.urun_fiyati:.2f} TL"

            c.drawString(inch, y_pos, urun_adi)
            c.drawString(inch * 4.2, y_pos, miktar)
            c.drawString(inch * 5.2, y_pos, birim_fiyat)
            c.drawString(inch * 6.7, y_pos, toplam_fiyat)
            y_pos -= 0.3 * inch

        # ---- Genel Toplam ----
        c.line(inch, y_pos, width - inch, y_pos)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(inch * 5, y_pos - 0.5 * inch, "Genel Toplam:")
        c.drawString(inch * 6.5, y_pos - 0.5 * inch, f"{siparis.toplam_tutar:.2f} TL")

        # PDF'i kaydet
        c.save()

        # 4. Veritabanına Fatura kaydını oluştur
        yeni_fatura = models.Fatura(
            siparis_id=siparis.id,
            fatura_yolu=dosya_yolu
        )
        db.add(yeni_fatura)
        db.commit()
        db.refresh(yeni_fatura)

        log.info(f"Sipariş {siparis.id} için fatura oluşturuldu: {dosya_yolu}")
        return yeni_fatura

    except Exception as e:
        # Hata olursa veritabanı işlemini geri al ve logla
        db.rollback()
        log.error(f"Fatura oluşturma hatası (Sipariş ID: {siparis.id}): {e}")
        # Bu hata, siparişin oluşmasını engellememeli.
        # Sadece loglayıp geçebiliriz veya yöneticiye bildirim gönderebiliriz.
        return None