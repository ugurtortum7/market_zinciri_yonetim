# app/main.py

from fastapi import FastAPI, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.db.base_class import Base
import json
from typing import Dict, Any
from fastapi.middleware.cors import CORSMiddleware

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
from app.models.fatura import Fatura


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
    gorevler_api
)

app = FastAPI(title="Market Yönetim")

# Startup'da tabloları oluştur
@app.on_event("startup")
def create_tables():
    """Uygulama başlarken tabloları oluştur"""
    Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "MY-SİS API + PostgreSQL çalışıyor!"}

# ---- Yeni Admin Fonksiyonları ----

@app.post("/admin/import-data")
async def import_data(file: UploadFile = File(...)):
    """JSON dosyasından verileri PostgreSQL'e import et"""
    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="Sadece JSON dosyaları kabul edilir")
    
    try:
        content = await file.read()
        data = json.loads(content.decode('utf-8'))
        db = SessionLocal()
        imported_tables = {}

        # JSON anahtarlarını model sınıflarına eşle
        model_map = {
            "kullanicilar": User,
            "lokasyonlar": Lokasyon,
            "urunler": Urun,
            "stoklar": Stok,
            "sevkiyatlar": Sevkiyat,
            "sevkiyat_detaylari": SevkiyatDetay,
            "satislar": Satis,
            "satis_detaylari": SatisDetay,
            "favoriler": Favori,
            "sepetler": Sepet,
            "sepet_urunleri": SepetUrunu,
            "siparisler": Siparis,
            "siparis_detaylari": SiparisDetay,
            "faturalar": Fatura,
        }

        for table_name, records in data.items():
            try:
                print(f"Import ediliyor: {table_name}")
                Model = model_map.get(table_name)
                if not Model:
                    imported_tables[table_name] = "Eşleşen model bulunamadı"
                    continue

                imported_count = 0
                for record in records:
                    obj = Model(**record)
                    db.add(obj)
                    imported_count += 1

                imported_tables[table_name] = imported_count
                print(f"  {imported_count} kayıt import edildi")

            except Exception as e:
                print(f"Hata - {table_name}: {str(e)}")
                imported_tables[table_name] = f"Hata: {str(e)}"
        
        db.commit()
        db.close()

        return {
            "message": "Import işlemi tamamlandı",
            "imported_tables": imported_tables,
            "total_tables": len(imported_tables)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import hatası: {str(e)}")


@app.get("/admin/table-info")
def get_table_info():
    """Mevcut tablo bilgilerini getir"""
    try:
        db = SessionLocal()
        result = db.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = [row[0] for row in result]
        table_counts = {}
        for table in tables:
            count_result = db.execute(f"SELECT COUNT(*) FROM {table}")
            table_counts[table] = count_result.scalar()
        db.close()
        return {
            "tables": table_counts,
            "total_tables": len(tables)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tablo bilgisi alınamadı: {str(e)}")

@app.get("/api/cron")
def cron_endpoint():
    """Cron job endpoint'i"""
    from datetime import datetime
    return {
        "status": "success",
        "message": "Cron job çalıştı",
        "timestamp": datetime.now().isoformat(),
        "database": "PostgreSQL"
    }

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


origins = [
    "http://localhost:5173",
    "https://market-front-psi.vercel.app"  # Sondaki / olmadan
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # sadece bu adreslerden gelen istekler kabul edilir
    allow_credentials=True,
    allow_methods=["*"],     # GET, POST, PUT, DELETE vb.
    allow_headers=["*"],     # Content-Type, Authorization vb.
)