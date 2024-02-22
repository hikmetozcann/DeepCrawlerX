import signal
import sys
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from urllib.parse import urlparse, urljoin
import json

class DeepCrawler:
    def __init__(self, base_url, max_threads=10, pause_every_n_pages=100):
        self.base_url = base_url
        self.domain_name = urlparse(base_url).netloc
        self.visited_urls = set()
        self.data = {
            "titles": set(),
            "paragraphs": set(),
            "images": set(),
            "meta": {},
            "social_media": {},
            "forms": [],
            "videos": set(),
            "links": set()
        }
        self.max_threads = max_threads
        self.pause_every_n_pages = pause_every_n_pages
        # ThreadPoolExecutor'ı başlat
        self.executor = ThreadPoolExecutor(max_workers=self.max_threads)

    def fetch(self, url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.content
        except Exception as e:
            print(f"Error fetching {url}: {e}")
        return None
    
    def pause_and_save(self):
        """Programı duraklatır, verileri kaydeder ve kullanıcıdan devam etmesini ister."""
        self.save_data()  # Mevcut verileri kaydet
        print("Veriler kaydedildi. Devam etmek için 'c' tuşlayın veya çıkmak için 'q': ", end='')
        self.executor.shutdown(wait=True)
        action = input().strip().lower()
        if action == 'q':
            print("Program sonlandırıldı.")
            exit()
            quit()

    def process_page(self, url, html):
        """Çekilen sayfanın içeriğini işler ve toplanan verileri kaydeder."""
        soup = BeautifulSoup(html, 'html.parser')

        # Sayfanın başlıklarını topla
        self.data["titles"].update(title.text.strip() for title in soup.find_all(['h1', 'h2', 'h3']))

        # Sayfanın paragraflarını topla
        self.data["paragraphs"].update(paragraph.text.strip() for paragraph in soup.find_all('p'))

        # Sayfadaki resimlerin URL'lerini topla
        self.data["images"].update(urljoin(url, img['src']) for img in soup.find_all('img') if img.get('src'))

        # Meta etiketlerini topla
        for meta in soup.find_all('meta'):
            key = meta.get('name') or meta.get('property')
            value = meta.get('content')
            if key:
                self.data["meta"][key] = value

        # Sosyal medya etiketlerini topla
        for meta in soup.find_all('meta'):
            if meta.get('property') and meta.get('property').startswith(('og:', 'twitter:')):
                self.data["social_media"][meta.get('property')] = meta.get('content')

        # Form bilgilerini topla
        for form in soup.find_all('form'):
            form_details = {
                "action": form.get('action'),
                "method": form.get('method', 'get').upper(),
                "inputs": [{input.get('name'): input.get('type', 'text')} for input in form.find_all('input')]
            }
            self.data["forms"].append(form_details)

        # Video URL'lerini topla
        self.data["videos"].update(urljoin(url, video['src']) for video in soup.find_all('video') if video.get('src'))

        # Sayfadaki tüm linkleri topla ve işle
        for link in soup.find_all('a', href=True):
            link_url = urljoin(url, link['href'])
            if urlparse(link_url).netloc == self.domain_name:
                self.data["links"].add(link_url)

    def scrape_url(self, url):
        if url in self.visited_urls or urlparse(url).netloc != self.domain_name:
            return
        print(f"Scraping {url}")
        self.visited_urls.add(url)
        if len(self.visited_urls) % self.pause_every_n_pages == 0:
            self.pause_and_save()

        html = self.fetch(url)
        self.process_page(url, html)

        # Use ThreadPoolExecutor to scrape pages in parallel
        links_to_scrape = [link for link in self.data["links"] if link not in self.visited_urls]
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = [executor.submit(self.scrape_url, link) for link in links_to_scrape]
            for future in as_completed(futures):
                future.result()  # Wait for all threads to complete

    def save_data(self):
        # Convert sets to lists for JSON serialization
        for key in self.data:
            if isinstance(self.data[key], set):
                self.data[key] = list(self.data[key])
        with open('scraped_data.json', 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

def handle_exit_signal(signal_received, frame, crawler):
    print("\nProgram durduruluyor, veriler kaydediliyor...")
    crawler.save_data()
    crawler.executor.shutdown(wait=True)
    print("İşlem tamamlandı.")
    exit(0)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        crawler = DeepCrawler(f"http://{sys.argv[1]}", max_threads=1)
        # Sinyal işleyicisini ayarla
        signal.signal(signal.SIGINT, lambda signal_received, frame: handle_exit_signal(signal_received, frame, crawler))

        try:
            crawler.scrape_url(crawler.base_url)
        finally:
            # CTRL+C basılmadığı durumlarda da verilerin kaydedilmesini sağlar
            crawler.save_data()
            crawler.executor.shutdown(wait=True)
            
    else:  
        print("Kullanım: python main.py <URL>")