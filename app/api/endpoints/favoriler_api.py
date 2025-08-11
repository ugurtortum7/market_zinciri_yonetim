from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas, services
from app.api import dependencies
from app.db.session import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.Favori])
def read_kullanicinin_favorileri(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """
    O an giriş yapmış olan kullanıcının favori listesini, ürün detaylarıyla
    birlikte döndürür.
    """
    return services.favoriler_service.get_kullanicinin_favorileri(
        db=db, kullanici_id=current_user.id
    )

@router.post("/{urun_id}", response_model=schemas.Favori)
def favoriye_ekle(
    urun_id: int,
    favori_data: schemas.FavoriCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """
    Belirtilen ID'ye sahip ürünü, o an giriş yapmış kullanıcının favorilerine ekler.
    Eğer ürün zaten favorilerde ise, mevcut kaydı döndürür.
    """
    # Ürünün var olup olmadığını kontrol etmek iyi bir pratiktir (şimdilik atlıyoruz)
    # db_urun = services.urun_service.get_urun_by_id(db, urun_id=urun_id)
    # if not db_urun:
    #     raise HTTPException(status_code=404, detail="Ürün bulunamadı.")
    
    return services.favoriler_service.favoriye_ekle(
        db=db, 
        kullanici_id=current_user.id, 
        urun_id=urun_id, 
        favori_data=favori_data
    )

@router.delete("/{urun_id}", status_code=status.HTTP_204_NO_CONTENT)
def favoriden_cikar(
    urun_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """
    Belirtilen ID'ye sahip ürünü, o an giriş yapmış kullanıcının favorilerinden siler.
    """
    # Silmeden önce, kaydın gerçekten var olup olmadığını kontrol etmeliyiz.
    favori_kaydi = services.favoriler_service.get_favori_by_kullanici_and_urun(
        db=db, kullanici_id=current_user.id, urun_id=urun_id
    )
    
    # Eğer kayıt bulunamazsa, 404 Hatası döndür. Bu, kullanıcıya
    # zaten favorilerinde olmayan bir şeyi silmeye çalıştığını bildirir.
    if not favori_kaydi:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favori kaydı bulunamadı.")
    
    # Kayıt bulunduysa, silme servisini çağır.
    services.favoriler_service.favoriden_cikar(db=db, favori_kaydi=favori_kaydi)
    
    # 204 durum kodu, "İşlem başarılı ve dönecek bir içerik yok" anlamına gelir.
    # Bu yüzden bir return ifadesi kullanmıyoruz.
    return Response(status_code=status.HTTP_204_NO_CONTENT)