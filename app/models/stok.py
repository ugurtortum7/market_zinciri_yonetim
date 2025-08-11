from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Stok(Base):
    __tablename__ = "stoklar"

    id = Column(Integer, primary_key=True, index=True)
    miktar = Column(Integer, nullable=False, default=0)
    kritik_seviye = Column(Integer, nullable=True)
    lokasyon_id = Column(Integer, ForeignKey("lokasyonlar.id"), nullable=False)
    urun_id = Column(Integer, ForeignKey("urunler.id"), nullable=False)
    lokasyon = relationship("Lokasyon")
    urun = relationship("Urun")
    __table_args__ = (UniqueConstraint('lokasyon_id', 'urun_id', name='_lokasyon_urun_uc'),)