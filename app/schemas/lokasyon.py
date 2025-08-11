from pydantic import BaseModel

class LokasyonBase(BaseModel):
    ad: str
    tip: str

class LokasyonCreate(LokasyonBase):
    pass

class Lokasyon(LokasyonBase):
    id: int

    class Config:
        from_attributes = True