from sqlalchemy import Column, Integer, String
from app.db.base_class import Base

class Lokasyon(Base):
    __tablename__ = "lokasyonlar"

    id = Column(Integer, primary_key=True, index=True)
    ad = Column(String(100), nullable=False)
    tip = Column(String(20), nullable=False)