from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate

def get_user_by_username(db: Session, username: str):
    """
    Veritabanından kullanıcı adına göre kullanıcıyı getirir.
    """
    return db.query(User).filter(User.kullanici_adi == username).first()

def create_user(db: Session, user: UserCreate):
    """
    Yeni bir kullanıcı oluşturur.
    """
    hashed_password = get_password_hash(user.password)
    db_user = User(
        kullanici_adi=user.kullanici_adi,
        hashlenmis_sifre=hashed_password,
        rol=user.rol,
        lokasyon_id=user.lokasyon_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user