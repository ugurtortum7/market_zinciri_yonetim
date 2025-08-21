# app/api/endpoints/kategoriler.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.kategori import Kategori, KategoriCreate
from app.services import kategori_service
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[Kategori])
def read_kategoriler(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Tüm kategorileri listeler. (Herkese açık)
    """
    kategoriler = kategori_service.get_kategoriler(db, skip=skip, limit=limit)
    return kategoriler

@router.post("/", response_model=Kategori)
def create_kategori(
    *,
    db: Session = Depends(deps.get_db),
    kategori_in: KategoriCreate,
    current_user: User = Depends(deps.get_current_active_manager_user),
):
    """
    Yeni bir kategori oluşturur. (Yönetici Korumalı)
    """
    kategori = kategori_service.get_kategori_by_ad(db, ad=kategori_in.ad)
    if kategori:
        raise HTTPException(
            status_code=400,
            detail="Bu kategori adı zaten mevcut.",
        )
    kategori = kategori_service.create_kategori(db=db, kategori=kategori_in)
    return kategori