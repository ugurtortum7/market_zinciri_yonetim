from fastapi import FastAPI, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.db.base_class import Base
import json
from typing import Dict, Any
from fastapi.middleware.cors import CORSMiddleware
from app.schemas.user import UserCreate
from app.services import user_service
from app.models.user import User
from app.models.lokasyon import Lokasyon
from app.models.urun import Urun
from app.models.stok import Stok
from app.models.sevkiyat import Sevkiyat, SevkiyatDetay
from app.models.satis import Satis, SatisDetay
from app.models.favoriler import Favori
from app.models.sepet import Sepet, SepetUrunu
from app.models.siparis import Siparis, SiparisDetay
from app.models.fatura import Fatura
from app.core import cloudinary_config

# API Router'lar
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
    gorevler_api,
    kategoriler,
    upload
)

app = FastAPI(title="Market Yönetim")

# ===== DEĞİŞİKLİK: Startup fonksiyonu güncellendi =====
@app.on_event("startup")
def on_startup():
    """
    Uygulama başlarken çalışır:
    1. Tabloları oluşturur.
    2. Varsayılan bir yönetici kullanıcısı olup olmadığını kontrol eder, yoksa oluşturur.
    """
    # 1. Tabloları oluştur
    Base.metadata.create_all(bind=engine)
    
    # 2. Varsayılan yöneticiyi oluştur
    db = SessionLocal()
    try:
        # 'YONETICI' rolünde bir kullanıcı var mı diye kontrol et
        admin_user = db.query(User).filter(User.rol == "YONETICI").first()
        
        if not admin_user:
            print("Yönetici kullanıcı bulunamadı, varsayılan yönetici oluşturuluyor...")
            # Varsayılan lokasyon yoksa oluştur (ID=1)
            default_location = db.query(Lokasyon).filter(Lokasyon.id == 1).first()
            if not default_location:
                 db.add(Lokasyon(id=1, ad="Merkez Depo", tip="DEPO"))
                 db.commit()

            # Yeni yönetici için şema oluştur
            user_in = UserCreate(
                kullanici_adi="admin",
                password="admin123", # Giriş yaptıktan sonra bu şifreyi değiştirmeniz önerilir
                rol="YONETICI",
                lokasyon_id=1
            )
            # user_service aracılığıyla kullanıcıyı oluştur (şifre hash'lenecek)
            user_service.create_user(db=db, user=user_in)
            print("Varsayılan yönetici (kullanıcı adı: admin, şifre: admin123) oluşturuldu.")
        else:
            print("Yönetici kullanıcısı zaten mevcut.")
            
    finally:
        db.close()
# ===== DEĞİŞİKLİK BİTTİ =====


@app.get("/")
def read_root():
    return {"message": "MY-SİS API + PostgreSQL çalışıyor!"}

# ---- Yeni Admin Fonksiyonları ----
# ... (dosyanın geri kalanı olduğu gibi kalıyor) ...
@app.post("/admin/import-data")
async def import_data(file: UploadFile = File(...)):
    # ...
    pass

@app.get("/admin/table-info")
def get_table_info():
    # ...
    pass

@app.get("/api/cron")
def cron_endpoint():
    # ...
    pass

# ---- Var olan router'ları ekle ----
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
app.include_router(gorevler_api.router, prefix="/gorevler", tags=["Zamanlanmış Görevler"])
app.include_router(kategoriler.router, prefix="/kategoriler", tags=["Kategori Yönetimi"])
app.include_router(upload.router, prefix="/upload", tags=["Dosya Yükleme"])

origins = [
    "http://localhost:5173",
    "https://market-front-psi.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)