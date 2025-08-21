# app/models/urun.py

from sqlalchemy import Column, Integer, String, Text, Float
from sqlalchemy.orm import relationship

from app.db.base_class import Base # <-- Bu satır ayrıldı ve düzeltildi

class Urun(Base):
    __tablename__ = "urunler"

    id = Column(Integer, primary_key=True, index=True)
    urun_adi = Column(String(150), nullable=False)
    sku = Column(String(50), unique=True, index=True, nullable=False)
    aciklama = Column(Text, nullable=True)
    resim_url = Column(String(255), nullable=True)

    # === YENİ EKLENEN SÜTUNLAR ===
    fiyat = Column(Float, nullable=False)
    marka = Column(String(100), nullable=False)
    birim = Column(String(50), nullable=False)
    kategori = Column(String(100), nullable=False)
    # =============================

    favoriler = relationship("Favori", back_populates="urun")