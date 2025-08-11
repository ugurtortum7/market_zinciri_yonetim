from pydantic import BaseModel
from typing import Optional

from .urun import Urun
from .lokasyon import Lokasyon

class StokBase(BaseModel):
    miktar: int
    lokasyon_id: int
    urun_id: int

class StokCreate(StokBase):
    pass

class Stok(StokBase):
    id: int
    kritik_seviye: Optional[int] = None
    
    urun: Urun
    lokasyon: Lokasyon

    class Config:
        from_attributes = True

class StokUpdateKritikSeviye(BaseModel):
    kritik_seviye: int