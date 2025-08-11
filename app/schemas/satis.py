from pydantic import BaseModel, Field
from typing import List

class SatisUrunCreate(BaseModel):
    urun_id: int
    miktar: int = Field(..., gt=0)
    satis_fiyati: float = Field(..., gt=0)

class SatisCreate(BaseModel):
    urunler: List[SatisUrunCreate]