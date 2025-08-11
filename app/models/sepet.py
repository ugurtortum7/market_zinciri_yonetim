# app/models/sepet.py

from sqlalchemy import (
    Column, 
    Integer, 
    DateTime, 
    ForeignKey, 
    UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class Sepet(Base):
    """
    Her kullanıcı için tek olan ana sepet kaydını temsil eder.
    """
    __tablename__ = "sepetler"

    id = Column(Integer, primary_key=True, index=True)
    
    # Bir kullanıcının sadece bir sepeti olabileceği için bu alanı
    # 'unique=True' olarak ayarlıyoruz.
    kullanici_id = Column(Integer, ForeignKey("kullanicilar.id"), unique=True, nullable=False)
    
    olusturulma_tarihi = Column(DateTime(timezone=True), server_default=func.now())
    # onupdate=func.now(), bu kayıt her güncellendiğinde bu alanın
    # otomatik olarak güncellenmesini sağlar.
    guncellenme_tarihi = Column(DateTime(timezone=True), onupdate=func.now())

    # İlişkiler
    kullanici = relationship("User")
    
    # Bir sepet silindiğinde, içindeki tüm ürünlerin de silinmesini sağlar.
    urunler = relationship(
        "SepetUrunu", 
        back_populates="sepet", 
        cascade="all, delete-orphan"
    )

class SepetUrunu(Base):
    """
    Bir sepetteki tek bir ürün satırını (ürün ve miktarı) temsil eder.
    """
    __tablename__ = "sepet_urunleri"

    id = Column(Integer, primary_key=True, index=True)
    miktar = Column(Integer, nullable=False)

    sepet_id = Column(Integer, ForeignKey("sepetler.id"), nullable=False)
    urun_id = Column(Integer, ForeignKey("urunler.id"), nullable=False)

    # İlişkiler
    sepet = relationship("Sepet", back_populates="urunler")
    urun = relationship("Urun")

    # Bir sepette aynı üründen iki farklı satır olmasını engeller.
    __table_args__ = (
        UniqueConstraint('sepet_id', 'urun_id', name='_sepet_urun_uc'),
    )