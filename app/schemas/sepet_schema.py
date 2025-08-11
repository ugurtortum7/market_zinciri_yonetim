from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
from .urun import Urun

class SepetUrunuBase(BaseModel):
    urun_id: int
    miktar: int = Field(..., gt=0)

class SepetUrunuCreate(SepetUrunuBase):
    pass

class SepetUrunu(BaseModel):
    miktar: int
    urun: Urun

    class Config:
        from_attributes = True

class Sepet(BaseModel):
    id: int
    guncellenme_tarihi: datetime
    urunler: List[SepetUrunu] = []
    toplam_tutar: float = 0.0

    class Config:
        from_attributes = True

class SepetUrunuUpdate(BaseModel):
    urun_id: int
    yeni_miktar: int = Field(..., ge=0)
