from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class Sevkiyat(Base):
    __tablename__ = "sevkiyatlar"

    id = Column(Integer, primary_key=True, index=True)
    sevkiyat_tarihi = Column(DateTime(timezone=True), server_default=func.now())
    
    kaynak_lokasyon_id = Column(Integer, ForeignKey("lokasyonlar.id"), nullable=False)
    hedef_lokasyon_id = Column(Integer, ForeignKey("lokasyonlar.id"), nullable=False)

    sevkiyat_detaylari = relationship("SevkiyatDetay", back_populates="sevkiyat")
    
    kaynak_lokasyon = relationship("Lokasyon", foreign_keys=[kaynak_lokasyon_id])
    hedef_lokasyon = relationship("Lokasyon", foreign_keys=[hedef_lokasyon_id])


class SevkiyatDetay(Base):
    __tablename__ = "sevkiyat_detaylari"

    id = Column(Integer, primary_key=True, index=True)
    miktar = Column(Integer, nullable=False)

    sevkiyat_id = Column(Integer, ForeignKey("sevkiyatlar.id"), nullable=False)
    urun_id = Column(Integer, ForeignKey("urunler.id"), nullable=False)

    sevkiyat = relationship("Sevkiyat", back_populates="sevkiyat_detaylari")
    urun = relationship("Urun")