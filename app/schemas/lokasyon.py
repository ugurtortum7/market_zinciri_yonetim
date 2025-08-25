# app/schemas/lokasyon.py

from pydantic import BaseModel
from typing import Optional

class LokasyonBase(BaseModel):
    ad: str
    tip: str

class LokasyonCreate(LokasyonBase):
    pass

class Lokasyon(LokasyonBase):
    id: int

    # YENİ EKLENEN KISIM: Bu satır, SQLAlchemy modelinden
    # Pydantic şemasına otomatik dönüşümü sağlar.
    class Config:
        from_attributes = True