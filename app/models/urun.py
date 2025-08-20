from sqlalchemy import Column, Integer, String, Text
from app.db.base_class import Base
from sqlalchemy.orm import relationship

class Urun(Base):
    __tablename__ = "urunler"

    id = Column(Integer, primary_key=True, index=True)
    urun_adi = Column(String(150), nullable=False)
    sku = Column(String(50), unique=True, index=True, nullable=False)
    aciklama = Column(Text, nullable=True)
    resim_url = Column(String(255), nullable=True)

    favoriler = relationship("Favori", back_populates="urun")