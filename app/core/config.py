import os
from dotenv import load_dotenv

# Bu komut, proje ana dizinindeki .env dosyasını bulur ve
# içindeki değişkenleri ortam değişkeni olarak yükler.
load_dotenv()

# Artık tüm ayarları hard-coded yazmak yerine, os.getenv() ile
# ortam değişkenlerinden (yani .env dosyasından) okuyoruz.
DB_SERVER = os.getenv("DB_SERVER")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_DRIVER = os.getenv("DB_DRIVER")

# Eğer .env dosyasında bu değişkenler yoksa, varsayılan bir değer atayabiliriz.
# Ama bizim dosyamızda hepsi var.
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
# os.getenv string döndürdüğü için, sayıyı int'e çeviriyoruz.
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# Veritabanı bağlantı cümlesi (DATABASE_URL) artık bu değişkenlerden oluşuyor.
DATABASE_URL = f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}?driver={DB_DRIVER}"