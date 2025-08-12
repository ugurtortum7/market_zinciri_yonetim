from pydantic import BaseModel, EmailStr
from typing import Optional

from .lokasyon import Lokasyon

class UserBase(BaseModel):
    kullanici_adi: str
    email: Optional[str] = None
    rol: str
    lokasyon_id: int

class UserCreate(UserBase):
    password: str 

class User(UserBase):
    id: int
    aktif: bool
    lokasyon: Optional[Lokasyon] = None

    class Config:
        from_attributes = True