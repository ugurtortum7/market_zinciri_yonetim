# app/schemas/urun.py

from pydantic import BaseModel
from typing import Optional

class UrunBase(BaseModel):
    urun_adi: str
    sku: str
    aciklama: Optional[str] = None
    resim_url: Optional[str] = None
    fiyat: float
    marka: str
    birim: str
    kategori: str

class UrunCreate(UrunBase):
    pass

# YENİ EKLENEN ŞEMA
class UrunUpdate(BaseModel):
    urun_adi: Optional[str] = None
    sku: Optional[str] = None
    aciklama: Optional[str] = None
    resim_url: Optional[str] = None
    fiyat: Optional[float] = None
    marka: Optional[str] = None
    birim: Optional[str] = None
    kategori: Optional[str] = None

class Urun(UrunBase):
    id: int

    class Config:
        from_attributes = True