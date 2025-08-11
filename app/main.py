# app/main.py

from fastapi import FastAPI

from app.db.base_class import Base
from app.db.session import engine

# Modeller
from app.models.user import User
from app.models.lokasyon import Lokasyon
from app.models.urun import Urun
from app.models.stok import Stok
from app.models.sevkiyat import Sevkiyat, SevkiyatDetay
from app.models.satis import Satis, SatisDetay
from app.models.favoriler import Favori
from app.models.sepet import Sepet, SepetUrunu
from app.models.siparis import Siparis, SiparisDetay

# API Router'ları
from app.api.endpoints import (
    auth, 
    kullanicilar, 
    lokasyonlar, 
    urunler, 
    stoklar, 
    sevkiyatlar, 
    satislar, 
    favoriler_api,
    sepet_api,
    siparis_api,
    gorevler_api  # Yeni görevler router'ı eklendi
)

def create_tables():
    Base.metadata.create_all(bind=engine)

app = FastAPI(title="Damla <3 Ugur")

@app.on_event("startup")
def on_startup():
    create_tables()

# Tüm router'ları uygulamaya dahil et
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(kullanicilar.router, prefix="/kullanicilar", tags=["Kullanıcı Yönetimi"])
app.include_router(lokasyonlar.router, prefix="/lokasyonlar", tags=["Lokasyonlar"])
app.include_router(urunler.router, prefix="/urunler", tags=["Ürün Yönetimi"])
app.include_router(stoklar.router, prefix="/stoklar", tags=["Stok Yönetimi"])
app.include_router(sevkiyatlar.router, prefix="/sevkiyatlar", tags=["Sevkiyat İşlemleri"])
app.include_router(satislar.router, prefix="/satislar", tags=["Satış İşlemleri"])
app.include_router(favoriler_api.router, prefix="/favoriler", tags=["Favoriler"])
app.include_router(sepet_api.router, prefix="/sepet", tags=["Sepet"])
app.include_router(siparis_api.router, prefix="/siparisler", tags=["Siparişler"])
app.include_router(gorevler_api.router, prefix="/gorevler", tags=["Zamanlanmış Görevler"]) # Yeni router eklendi

@app.get("/")
def read_root():
    return {"message": "MY-SİS API'ye hoş geldiniz!"}