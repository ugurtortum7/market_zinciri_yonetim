from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas, models, services
from app.api import dependencies
from app.db.session import get_db

router = APIRouter()

@router.post("/", response_model=schemas.User)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_manager: models.User = Depends(dependencies.get_current_manager_user)
):
    """
    Yeni bir kullanıcı (Yönetici veya Kasiyer) oluşturur.
    Sadece yetkili Yöneticiler tarafından erişilebilir.
    """
    db_user = services.user_service.get_user_by_username(db, username=user.kullanici_adi)
    if db_user:
        raise HTTPException(status_code=400, detail="Bu kullanıcı adı zaten kayıtlı.")
    
    return services.user_service.create_user(db=db, user=user)