import signal
import sys
from crawler import DeepCrawler
from data_manager import save_data

def signal_handler(sig, frame):
    print('Program durduruluyor, veriler kaydediliyor...')
    crawler.save_data()  # Toplanan verileri kaydet
    sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
        crawler = DeepCrawler(base_url)

        # Sinyal yakalayıcıyı ayarla
        signal.signal(signal.SIGINT, signal_handler)

        try:
            crawler.scrape_url(base_url)
        finally:
            crawler.save_data()  # Program sonlandırıldığında verileri kaydet
    else:
        print("Usage: python main.py <URL>")
