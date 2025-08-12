import os
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL (Railway'den otomatik gelecek)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")  # Fallback SQLite

# Diğer ayarlar
SECRET_KEY = os.getenv("SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# SQL Server ayarları yorum satırına al (geçici)
# DB_SERVER = os.getenv("DB_SERVER")
# DB_USER = os.getenv("DB_USER")
# DB_PASSWORD = os.getenv("DB_PASSWORD")
# DB_NAME = os.getenv("DB_NAME")
# DB_DRIVER = os.getenv("DB_DRIVER")
# DATABASE_URL = f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}?driver={DB_DRIVER}"