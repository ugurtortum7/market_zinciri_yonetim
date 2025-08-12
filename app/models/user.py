from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class User(Base):
    __tablename__ = "kullanicilar"

    id = Column(Integer, primary_key=True, index=True)
    kullanici_adi = Column(String(50), unique=True, index=True, nullable=False)
    hashlenmis_sifre = Column(String(255), nullable=False)
    rol = Column(String(20), nullable=False)
    aktif = Column(Boolean, default=True)

    lokasyon_id = Column(Integer, ForeignKey("lokasyonlar.id"))

    lokasyon = relationship("Lokasyon")

    favoriler = relationship("Favori", back_populates="kullanici")