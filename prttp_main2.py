import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse, urljoin
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

class DeepCrawler:
    def __init__(self, base_url, max_threads=5):
        self.base_url = base_url
        self.domain_name = urlparse(base_url).netloc
        self.visited_urls = set()
        self.max_threads = max_threads
        self.data = {
            "links": [],
            "titles": [],
            "paragraphs": [],
            "images": [],
            "meta": {},
            "social_media": {},
            "forms": [],
            "videos": []
        }

    def scrape_url(self, url):
        if url in self.visited_urls or urlparse(url).netloc != self.domain_name:
            return
        print(f"Scraping {url}")
        self.visited_urls.add(url)

        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, "html.parser")

            # Meta verileri topla, sosyal medya etiketlerini topla, vb.
            # Veri toplama işlemleri...

            # Linkleri topla
            links = [urljoin(url, link['href']) for link in soup.find_all('a', href=True) if urlparse(urljoin(url, link['href'])).netloc == self.domain_name]

            self.data["links"].extend(links)

            # Yeni bulunan linkler için scrape_url fonksiyonunu tekrar çağırma
            with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
                futures = [executor.submit(self.scrape_url, link) for link in links if link not in self.visited_urls]
                for future in as_completed(futures):
                    future.result()  # Hataları yakalamak ve bekleyen işlemleri tamamlamak için

        except Exception as e:
            print(f"Error scraping {url}: {e}")

    def save_data(self):
        """Toplanan verileri JSON dosyasına kaydeder."""
        with open("scraped_data.json", "w", encoding='utf-8') as file:
            json.dump(self.data, file, indent=4, ensure_ascii=False)
        print("Veriler başarıyla kaydedildi.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
        crawler = DeepCrawler(base_url)
        crawler.scrape_url(base_url)
        crawler.save_data()
    else:
        print("Usage: python scraper.py <URL>")
