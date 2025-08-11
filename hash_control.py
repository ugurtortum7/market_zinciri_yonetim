# hash_kontrol.py (Güncellenmiş Hali)

from app.core.security import get_password_hash

# Yeni bir hash oluşturmak istediğimiz şifre
yeni_sifre = "admin123"

# Kendi sisteminde, kendi kütüphanelerinle yeni bir hash oluştur
yeni_hash = get_password_hash(yeni_sifre)

print("--- YENİ OLUŞTURULAN GÜVENLİ HASH ---")
print(yeni_hash)
print("--- LÜTFEN YUKARIDAKİ SATIRIN TAMAMINI KOPYALAYIN ---")