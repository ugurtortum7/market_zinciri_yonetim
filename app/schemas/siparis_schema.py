# app/schemas/siparis_schema.py

from pydantic import BaseModel
from typing import List
from datetime import datetime
from decimal import Decimal

from .urun import Urun

# Sipariş oluştururken kullanıcıdan sadece teslimat adresini alırız.
class SiparisCreate(BaseModel):
    teslimat_adresi: str

# API'den bir sipariş detayı dönerken kullanılacak şema.
class SiparisDetay(BaseModel):
    miktar: int
    urun_fiyati: Decimal
    urun: Urun  # İç içe şema ile ürünün tüm detayları

    class Config:
        from_attributes = True

# API'den bir siparişin tamamını dönerken kullanılacak ana şema.
class Siparis(BaseModel):
    id: int
    siparis_tarihi: datetime
    toplam_tutar: Decimal
    teslimat_adresi: str
    siparis_durumu: str
    detaylar: List[SiparisDetay] = []

    class Config:
        from_attributes = True