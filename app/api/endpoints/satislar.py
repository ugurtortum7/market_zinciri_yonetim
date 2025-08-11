from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import schemas, models, services
from app.api import dependencies
from app.db.session import get_db

router = APIRouter()

@router.post("/")
def create_satis(
    satis: schemas.SatisCreate,
    db: Session = Depends(get_db),
    current_cashier: models.User = Depends(dependencies.get_current_cashier_user)
):
    """
    Yeni bir satış işlemi oluşturur.
    Bu işlem stokları otomatik olarak düşürür ve gerekirse otomatik sevkiyat tetikler.
    Sadece Kasiyerler erişebilir.
    """
    return services.satis_service.create_satis(
        db=db, satis_data=satis, kasiyer=current_cashier
    )