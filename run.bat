@echo off
REM Pencere basligini ayarla
title MY-SIS API Sunucusu

REM Bu .bat dosyasinin bulundugu dizine gec
cd /d "%~dp0"

echo Sanal ortam (venv) kontrol ediliyor...
IF NOT EXIST ".\venv\Scripts\activate" (
    echo HATA: 'venv' sanal ortami bu dizinde bulunamadi.
    echo Lutfen 'python -m venv venv' komutuyla olusturdugunuzdan emin olun.
    pause
    exit /b
)

echo Sanal ortam (venv) aktive ediliyor...
call .\venv\Scripts\activate

echo.
echo FastAPI/Uvicorn sunucusu baslatiliyor...
echo Adres: http://127.0.0.1:8000
echo Otomatik Dokumantasyon (Swagger): http://127.0.0.1:8000/docs
echo Otomatik Dokumantasyon (ReDoc): http://127.0.0.1:8000/redoc
echo.
echo Sunucuyu durdurmak icin bu pencerede CTRL+C tusuna basin.
echo.

uvicorn app.main:app --reload

echo.
echo Sunucu durduruldu.
pause