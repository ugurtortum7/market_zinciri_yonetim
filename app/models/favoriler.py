from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class Favori(Base):
    __tablename__ = "favoriler"

    id = Column(Integer, primary_key=True,index=True)
    kullanici_id = Column(Integer, ForeignKey("kullanicilar.id"), nullable=False)
    urun_id = Column(Integer, ForeignKey("urunler.id"), nullable=False)
    bildirim_istiyor_mu = Column(Boolean, default=False, nullable=False)
    eklenme_tarihi = Column(DateTime(timezone=True), server_default=func.now())

    kullanici = relationship("User", back_populates="favoriler")
    urun = relationship("Urun", back_populates="favoriler")

    __table_args__ = (
        UniqueConstraint('kullanici_id', 'urun_id', name='_kullanici_urun_favori_uc'),
    )
