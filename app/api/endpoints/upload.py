# app/api/endpoints/upload.py
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, status
import cloudinary
import cloudinary.uploader

from app.api import deps
from app.models.user import User

router = APIRouter()

@router.post("/image/")
def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_active_manager_user) # Sadece yöneticiler yükleyebilir
):
    """
    Bir resim dosyasını alır, Cloudinary'e yükler ve URL'sini döndürür.
    """
    try:
        # Dosyayı Cloudinary'e yüklüyoruz
        result = cloudinary.uploader.upload(file.file)

        # Yükleme başarılıysa, güvenli URL'yi alıyoruz
        secure_url = result.get("secure_url")

        # Frontend'e bu URL'yi içeren bir JSON cevabı gönderiyoruz
        return {"url": secure_url}
    except Exception as e:
        # Bir hata olursa, 500 Internal Server Error hatası veriyoruz
        print(f"Cloudinary yükleme hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Resim yüklenirken bir sunucu hatası oluştu."
        )