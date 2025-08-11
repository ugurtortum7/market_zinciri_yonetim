from sqlalchemy import Column, Integer, ForeignKey, DateTime, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class Satis(Base):
    __tablename__ = "satislar"

    id = Column(Integer, primary_key=True, index=True)
    satis_tarihi = Column(DateTime(timezone=True), server_default=func.now())
    toplam_tutar = Column(DECIMAL(10, 2), nullable=False)
    
    lokasyon_id = Column(Integer, ForeignKey("lokasyonlar.id"), nullable=False)
    kasiyer_id = Column(Integer, ForeignKey("kullanicilar.id"), nullable=False)

    detaylar = relationship("SatisDetay", back_populates="satis")

class SatisDetay(Base):
    __tablename__ = "satis_detaylari"

    id = Column(Integer, primary_key=True, index=True)
    miktar = Column(Integer, nullable=False)
    satis_fiyati = Column(DECIMAL(10, 2), nullable=False)

    satis_id = Column(Integer, ForeignKey("satislar.id"), nullable=False)
    urun_id = Column(Integer, ForeignKey("urunler.id"), nullable=False)

    satis = relationship("Satis", back_populates="detaylar")
    urun = relationship("Urun")