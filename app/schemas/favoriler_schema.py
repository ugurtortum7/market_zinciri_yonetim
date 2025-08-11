from pydantic import BaseModel
from .urun import Urun

class FavoriBase(BaseModel):
    bildirim_istiyor_mu: bool = False

class FavoriCreate(FavoriBase):
    pass    





class Favori(FavoriBase):
    id: int
    urun: Urun

    class Config:
        from_attributes = True
