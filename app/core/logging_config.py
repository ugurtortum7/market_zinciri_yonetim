# app/core/logging_config.py

import logging
import sys
from logging.handlers import TimedRotatingFileHandler

# 1. Log Formatı
# Her log mesajının nasıl görüneceğini belirleyen bir şablon oluşturuyoruz.
# Tarih/Saat - Logger Adı - Log Seviyesi - Asıl Mesaj
FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")

# 2. Log Dosyasının Adı
# Tüm log kayıtlarımızın birikeceği dosyanın adını belirliyoruz.
LOG_FILE = "api.log"


def get_console_handler():
    """
    Bu fonksiyon, logları konsola (siyah terminal ekranına) yazdırmak için
    bir "handler" (işleyici) oluşturur.
    """
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler

def get_file_handler():
    """
    Bu fonksiyon, logları bir dosyaya yazdırmak için bir handler oluşturur.
    """
    # TimedRotatingFileHandler, çok özel ve güçlü bir handler'dır.
    # 'when="midnight"' parametresi sayesinde, her gece yarısı geldiğinde
    # mevcut log dosyasını arşivler (örn: api.log.2025-08-04) ve boş bir
    # api.log dosyası oluşturur. Bu, log dosyasının zamanla devasa boyutlara
    # ulaşmasını engeller.
    file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight', encoding='utf-8')
    file_handler.setFormatter(FORMATTER)
    return file_handler

def get_logger(logger_name: str) -> logging.Logger:
    """
    Bu, projemizin diğer dosyalarından çağıracağımız ana fonksiyondur.
    Bize, hem konsola hem de dosyaya yazacak şekilde yapılandırılmış
    bir logger nesnesi verir.
    """
    # logger_name parametresiyle (örn: "sevkiyat_servisi") bir logger oluşturuyoruz.
    logger = logging.getLogger(logger_name)
    
    # Log seviyesini DEBUG olarak ayarlıyoruz. Bu, INFO, WARNING, ERROR gibi
    # tüm seviyedeki mesajların bu logger tarafından işleme alınmasını sağlar.
    logger.setLevel(logging.DEBUG)

    # Oluşturduğumuz iki handler'ı da bu logger'a ekliyoruz.
    logger.addHandler(get_console_handler())
    logger.addHandler(get_file_handler())
    
    # Bu ayar, logların çift yazılmasını önlemek için önemlidir.
    logger.propagate = False

    return logger