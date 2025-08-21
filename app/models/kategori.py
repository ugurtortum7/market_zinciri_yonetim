# app/models/kategori.py
from sqlalchemy import Column, Integer, String
from app.db.base_class import Base

class Kategori(Base):
    __tablename__ = "kategoriler"

    id = Column(Integer, primary_key=True, index=True)
    ad = Column(String(100), unique=True, index=True, nullable=False)