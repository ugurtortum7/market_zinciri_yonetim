from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from app.models.favoriler import Favori
from app.schemas.favoriler_schema import FavoriCreate

def get_kullanicinin_favorileri(db: Session, kullanici_id: int) -> List[Favori]:
    """
    Belirli bir kullanıcının tüm favori kayıtlarını, ürün detaylarıyla birlikte
    verimli bir şekilde getirir.
    """
    return db.query(Favori).filter(Favori.kullanici_id == kullanici_id).options(joinedload(Favori.urun)).all()

def get_favori_by_kullanici_and_urun(db: Session, kullanici_id: int, urun_id: int) -> Optional[Favori]:
    """
    Bir ürünün, bir kullanıcının favorilerinde zaten olup olmadığını kontrol eder.
    Eğer varsa, o favori kaydını döndürür. Yoksa, None döndürür.
    """
    return db.query(Favori).filter(Favori.kullanici_id == kullanici_id, Favori.urun_id == urun_id).first()

def favoriye_ekle(db: Session, kullanici_id: int, urun_id: int, favori_data: FavoriCreate) -> Favori:
    """
    Bir ürünü kullanıcının favorilerine ekler.
    Eğer ürün zaten favorilerde ise, yeni bir kayıt eklemez, mevcut kaydı döndürür.
    """
    mevcut_favori = get_favori_by_kullanici_and_urun(db, kullanici_id=kullanici_id, urun_id=urun_id)
    if mevcut_favori:
        return mevcut_favori

    yeni_favori = Favori(
        kullanici_id=kullanici_id,
        urun_id=urun_id,
        bildirim_istiyor_mu=favori_data.bildirim_istiyor_mu
    )
    
    db.add(yeni_favori)
    db.commit()
    db.refresh(yeni_favori)
    
    return yeni_favori

def favoriden_cikar(db: Session, favori_kaydi: Favori):
    """
    Verilen bir favori kaydını veritabanından siler.
    """
    db.delete(favori_kaydi)
    db.commit()
    return {"message": "Favorilerden başarıyla kaldırıldı."}