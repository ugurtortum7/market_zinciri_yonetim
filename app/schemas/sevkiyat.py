from pydantic import BaseModel, Field
from typing import List

class SevkiyatUrunCreate(BaseModel):
    urun_id: int
    miktar: int = Field(..., gt=0)
    
class SevkiyatCreate(BaseModel):
    hedef_lokasyon_id: int
    urunler: List[SevkiyatUrunCreate]

class SevkiyatUrun(BaseModel):
    urun_adi: str
    sku: str
    miktar: int

    class Config:
        from_attributes = True

class Sevkiyat(BaseModel):
    id: int
    kaynak_lokasyon_ad: str
    hedef_lokasyon_ad: str
    sevkiyat_tarihi: str
    detaylar: List[SevkiyatUrun]

    class Config:
        from_attributes = True