import json

DATA_FILE_PATH = 'data/scraped_data.json'

def save_data(data):
    """Toplanan verileri JSON dosyasına kaydeder."""
    try:
        with open(DATA_FILE_PATH, 'w', encoding='utf-8') as file:
            json.dump(list(data), file, indent=4, ensure_ascii=False)
        print("Veriler başarıyla kaydedildi.")
    except Exception as e:
        print(f"Verileri kaydederken bir hata oluştu: {e}")
