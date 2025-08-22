# app/core/cloudinary_config.py
import os
import cloudinary

# Railway'e eklediğimiz ortam değişkenlerini okuyoruz
cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
api_key = os.getenv("CLOUDINARY_API_KEY")
api_secret = os.getenv("CLOUDINARY_API_SECRET")

# Cloudinary kütüphanesini bu bilgilerle yapılandırıyoruz
cloudinary.config(
    cloud_name=cloud_name,
    api_key=api_key,
    api_secret=api_secret
)

print("Cloudinary yapılandırması yüklendi.")