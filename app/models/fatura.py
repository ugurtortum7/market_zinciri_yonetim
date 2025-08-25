# app/models/fatura.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base

class Fatura(Base):
    __tablename__ = "faturalar"

    id = Column(Integer, primary_key=True, index=True)
    siparis_id = Column(Integer, ForeignKey("siparisler.id"), unique=True, nullable=False)
    fatura_yolu = Column(String(255), nullable=False)
    olusturulma_tarihi = Column(DateTime, default=datetime.now)

    siparis = relationship("Siparis")