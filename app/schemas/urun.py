from pydantic import BaseModel
from typing import Optional

class UrunBase(BaseModel):
    urun_adi: str
    sku: str
    aciklama: Optional[str] = None
    resim_url: Optional[str] = None

class UrunCreate(UrunBase):
    pass

class Urun(UrunBase):
    id: int

    class Config:
        from_attributes = True