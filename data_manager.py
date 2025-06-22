import json
import os

DATA_DIR = "data"
DATA_FILE_PATH = os.path.join(DATA_DIR, "scraped_data.json")


def save_data(data):
    """Toplanan verileri JSON dosyasına kaydeder."""
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(DATA_FILE_PATH, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        print("Veriler başarıyla kaydedildi.")
    except Exception as e:
        print(f"Verileri kaydederken bir hata oluştu: {e}")
