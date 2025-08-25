# app/api/endpoints/siparis_api.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from fastapi.responses import StreamingResponse

from app import models, schemas, services
from app.api import dependencies
from app.db.session import get_db

router = APIRouter()

@router.post("/", response_model=schemas.Siparis)
def siparis_olustur(
    siparis_data: schemas.SiparisCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user),
):
    return services.siparis_service.create_order_from_cart(
        db=db, kullanici=current_user, siparis_data=siparis_data
    )

@router.get("/", response_model=List[schemas.Siparis])
def kullanici_siparislerini_listele(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user),
):
    return services.siparis_service.get_kullanici_siparisleri(
        db=db, kullanici_id=current_user.id
    )

@router.get("/{siparis_id}/fatura")
def faturayi_indir(
    siparis_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user),
):
    siparisler = services.siparis_service.get_kullanici_siparisleri(db=db, kullanici_id=current_user.id)
    tek_siparis = next((s for s in siparisler if s.id == siparis_id), None)
    
    if not tek_siparis:
        raise HTTPException(status_code=404, detail="Sipariş bulunamadı veya yetkiniz yok.")

    pdf_buffer = services.fatura_service.generate_invoice_pdf_in_memory(tek_siparis)

    if not pdf_buffer:
        raise HTTPException(status_code=500, detail="Fatura oluşturulurken bir sunucu hatası oluştu.")
    
    dosya_adi = f"fatura-siparis-{siparis_id}.pdf"
    headers = {'Content-Disposition': f'attachment; filename="{dosya_adi}"'}
    
    return StreamingResponse(pdf_buffer, media_type='application/pdf', headers=headers)