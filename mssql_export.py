import pyodbc
import json
import os
from datetime import datetime

def export_mssql_data():
    """MSSQL'den tüm tabloları export et"""
    
    # MSSQL bağlantısı
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=DESKTOP-K71VH7D\\SQLEXPRESS;"
        "DATABASE=my_sis_db;"
        "UID=sa;"
        "PWD=10443001"
    )
    
    cursor = conn.cursor()
    
    # Tüm tablo isimlerini al
    cursor.execute("""
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE'
    """)
    
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Bulunan tablolar: {tables}")
    
    export_data = {}
    
    for table_name in tables:
        print(f"Export ediliyor: {table_name}")
        
        # Tablo verilerini al
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        # Dictionary formatına çevir
        table_data = []
        for row in rows:
            row_dict = {}
            for i, value in enumerate(row):
                # Datetime objelerini string'e çevir
                if isinstance(value, datetime):
                    row_dict[columns[i]] = value.isoformat()
                else:
                    row_dict[columns[i]] = value
            table_data.append(row_dict)
        
        export_data[table_name] = table_data
        print(f"  {len(table_data)} kayıt export edildi")
    
    # JSON dosyasına kaydet
    filename = 'mssql_export_data.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)
    
    conn.close()
    print(f"\nTüm veriler {filename} dosyasına export edildi!")
    
    # Özet bilgiler
    total_records = sum(len(table_data) for table_data in export_data.values())
    print(f"Toplam {len(tables)} tablo, {total_records} kayıt export edildi")
    
    return filename

if __name__ == "__main__":
    try:
        export_mssql_data()
        print("Export işlemi başarıyla tamamlandı!")
    except Exception as e:
        print(f"Hata oluştu: {e}")
        input("Devam etmek için Enter'a basın...")