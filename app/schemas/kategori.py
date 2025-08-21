# app/schemas/kategori.py
from pydantic import BaseModel

class KategoriBase(BaseModel):
    ad: str

class KategoriCreate(KategoriBase):
    pass

class Kategori(KategoriBase):
    id: int

    class Config:
        from_attributes = True