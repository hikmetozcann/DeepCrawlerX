import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from data_manager import save_data

class DeepCrawler:
    def __init__(self, base_url):
        self.base_url = base_url
        self.domain_name = urlparse(base_url).netloc
        self.visited_urls = set()

    def scrape_url(self, url):
        if url in self.visited_urls or urlparse(url).netloc != self.domain_name:
            return
        print(f"Scraping {url}")
        self.visited_urls.add(url)

        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                self.process_page(url, soup)
                links = [urljoin(url, link.get('href')) for link in soup.find_all('a', href=True)]
                for link in links:
                    if urlparse(link).netloc == self.domain_name and link not in self.visited_urls:
                        self.scrape_url(link)
            else:
                print(f"Failed to retrieve {url}")
        except Exception as e:
            print(f"Error scraping {url}: {e}")

    def process_page(self, url, soup):
        """Çekilen sayfanın içeriğini işler ve toplanan verileri kaydeder."""
        
        # Sayfanın başlıklarını topla
        titles = {title.text.strip() for title in soup.find_all(['h1', 'h2', 'h3'])}
        
        # Sayfanın paragraflarını topla
        paragraphs = {paragraph.text.strip() for paragraph in soup.find_all('p')}
        
        # Sayfadaki resimlerin URL'lerini topla
        images = {urljoin(url, img['src']) for img in soup.find_all('img') if img.get('src')}
        
        # Meta etiketlerini topla
        meta_tags = {meta.get('name') or meta.get('property'): meta.get('content') for meta in soup.find_all('meta')}
        
        # Sosyal medya etiketlerini topla
        social_media_tags = {
            meta.get('property'): meta.get('content')
            for meta in soup.find_all('meta')
            if meta.get('property') and meta.get('property').startswith(('og:', 'twitter:'))
        }
        
        # Form bilgilerini topla
        forms = [{
            "action": form.get('action'),
            "method": form.get('method'),
            "inputs": [{input.get('name'): input.get('type')} for input in form.find_all('input')]
        } for form in soup.find_all('form')]
        
        # Video URL'lerini topla
        videos = {urljoin(url, video['src']) for video in soup.find_all('video') if video.get('src')}
        
        # Sayfadaki tüm linkleri topla
        links = {urljoin(url, link['href']) for link in soup.find_all('a', href=True)}
        
        # Toplanan verileri bir veri yapısında sakla
        page_data = {
            'url': url,
            'titles': list(titles),
            'paragraphs': list(paragraphs),
            'images': list(images),
            'meta': meta_tags,
            'social_media': social_media_tags,
            'forms': forms,
            'videos': list(videos),
            'links': list(links)
        }
        
        # Toplanan verileri kaydet
        self.save_data(page_data)


    def save_data(self):
        # Tüm tarama işlemi tamamlandığında, toplanan verileri kaydetmek için kullanılır.
        # Örneğin, tüm bağlantıları veya sayfa başlıklarını bir JSON dosyasına kaydedebilirsiniz.
        save_data(self.visited_urls)
