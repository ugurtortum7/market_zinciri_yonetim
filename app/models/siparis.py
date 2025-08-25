# app/models/siparis.py

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal

from app.db.base_class import Base

class Siparis(Base):
    __tablename__ = "siparisler"

    id = Column(Integer, primary_key=True, index=True)
    kullanici_id = Column(Integer, ForeignKey("kullanicilar.id"), nullable=False)
    siparis_tarihi = Column(DateTime, default=datetime.now)
    teslimat_adresi = Column(String, nullable=False)
    toplam_tutar = Column(Float(asdecimal=True), nullable=False)
    durum = Column(String, default="Hazırlanıyor")

    kullanici = relationship("User")
    
    detaylar = relationship("SiparisDetay", back_populates="siparis", cascade="all, delete-orphan")
    
    # DÜZELTME: 'Fatura' modelindeki 'siparis' ilişkisine geri bağlanıyor.
    fatura = relationship("Fatura", uselist=False, back_populates="siparis", cascade="all, delete-orphan")

class SiparisDetay(Base):
    __tablename__ = "siparis_detaylari"

    id = Column(Integer, primary_key=True, index=True)
    siparis_id = Column(Integer, ForeignKey("siparisler.id"), nullable=False)
    urun_id = Column(Integer, ForeignKey("urunler.id"), nullable=False)
    miktar = Column(Integer, nullable=False)
    urun_fiyati = Column(Float(asdecimal=True), nullable=False)

    siparis = relationship("Siparis", back_populates="detaylar")
    urun = relationship("Urun")