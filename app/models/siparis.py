from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class Siparis(Base):
    __tablename__ = "siparisler"

    id = Column(Integer, primary_key=True, index=True)
    siparis_tarihi = Column(DateTime(timezone=True), server_default=func.now())
    toplam_tutar = Column(DECIMAL(10, 2), nullable=False)
    teslimat_adresi = Column(String(255), nullable=False)
    siparis_durumu = Column(String(50), nullable=False, default="Hazırlanıyor")
    
    kullanici_id = Column(Integer, ForeignKey("kullanicilar.id"), nullable=False)

    kullanici = relationship("User")
    detaylar = relationship(
        "SiparisDetay", 
        back_populates="siparis", 
        cascade="all, delete-orphan"
    )

class SiparisDetay(Base):
    __tablename__ = "siparis_detaylari"

    id = Column(Integer, primary_key=True, index=True)
    miktar = Column(Integer, nullable=False)
    urun_fiyati = Column(DECIMAL(10, 2), nullable=False)

    siparis_id = Column(Integer, ForeignKey("siparisler.id"), nullable=False)
    urun_id = Column(Integer, ForeignKey("urunler.id"), nullable=False)

    siparis = relationship("Siparis", back_populates="detaylar")
    urun = relationship("Urun")