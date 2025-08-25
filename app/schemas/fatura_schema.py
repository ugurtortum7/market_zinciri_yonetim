# app/schemas/fatura_schema.py
from pydantic import BaseModel
from datetime import datetime

class FaturaBase(BaseModel):
    siparis_id: int
    fatura_yolu: str

class FaturaCreate(FaturaBase):
    pass

class Fatura(FaturaBase):
    id: int
    olusturulma_tarihi: datetime

    class Config:
        from_attributes = True