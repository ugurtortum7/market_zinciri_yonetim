from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class Fatura(Base):
    __tablename__ = "faturalar"

    id = Column(Integer, primary_key=True, index=True)
    fatura_yolu = Column(String(255), nullable=False, unique=True)
    olusturma_tarihi = Column(DateTime(timezone=True), server_default=func.now())

    # Her fatura bir siparişe aittir.
    siparis_id = Column(Integer, ForeignKey("siparisler.id"), nullable=False, unique=True)

    # Siparis modeli ile ilişki kuruyoruz.
    # `back_populates` sayesinde Siparis modelinden de Fatura'ya erişebileceğiz.
    siparis_detaylari = relationship("SiparisDetay", back_populates="fatura")