# app/api/endpoints/gorevler_api.py

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app import services
from app.db.session import get_db

# Güvenlik için kullanacağımız gizli anahtar.
# Profesyonel bir projede bu .env dosyasından okunmalıdır.
CRON_SECRET = "GecelikSevkiyatTetikleyici_Malatya44_!2025"

router = APIRouter()

@router.post("/tetikle-gunluk-sevkiyat")
def tetikle_sevkiyat(secret: str, db: Session = Depends(get_db)):
    """
    Zamanlanmış görevin (cron job) çağıracağı endpoint.
    Sadece doğru 'secret' query parametresi ile çalışır.
    Örnek Çağrı: POST /gorevler/tetikle-gunluk-sevkiyat?secret=...
    """
    if secret != CRON_SECRET:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Yetkisiz erişim."
        )
    
    # Not: Servis fonksiyonunu bir arka plan görevine de alabiliriz.
    # Bu, cronjob servisinin anında yanıt almasını sağlar.
    # from fastapi import BackgroundTasks
    # background_tasks.add_task(services.sevkiyat_service.tetikle_gunluk_sevkiyat, db)
    
    services.sevkiyat_service.tetikle_gunluk_sevkiyat(db=db)
    
    return {"message": "Günlük sevkiyat görevi başarıyla tetiklendi."}