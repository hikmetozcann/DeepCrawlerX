import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse, urljoin
import sys


def save_data(data):
    """Toplanan verileri JSON dosyasına kaydeder."""
    with open("scraped_data.json", "w", encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    print("Veriler başarıyla kaydedildi.")

def scrape_url(url):
    if url in visited_urls or urlparse(url).netloc != domain_name:
        return
    print(f"Scraping {url}")
    visited_urls.add(url)
    
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        
          # Meta verileri topla
        data["meta"][url] = {meta.get('name') or meta.get('property'): meta.get('content') 
                             for meta in soup.find_all('meta')}
        
        # Sosyal medya etiketlerini topla
        social_tags = ['og:', 'twitter:']
        data["social_media"][url] = {meta.get('property'): meta.get('content') 
                                      for meta in soup.find_all('meta') 
                                      if any(tag in (meta.get('property') or '') for tag in social_tags)}
        
        # Form bilgilerini topla
        forms = soup.find_all('form')
        for form in forms:
            form_data = {
                "action": form.get('action'),
                "method": form.get('method'),
                "inputs": [{input.get('name'): input.get('type')} for input in form.find_all('input')]
            }
            data["forms"].append(form_data)
        
        # Video ve multimedya öğelerini topla
        videos = soup.find_all('video')
        for video in videos:
            sources = video.find_all('source')
            data["videos"].extend([src.get('src') for src in sources])
        
        for title in soup.find_all(['h1', 'h2', 'h3']):
            title_text = title.text.strip()
            if title_text not in unique_titles:
                unique_titles.add(title_text)
                data["titles"].append(title_text)
        
        for paragraph in soup.find_all('p'):
            paragraph_text = paragraph.text.strip()
            if paragraph_text not in unique_paragraphs:
                unique_paragraphs.add(paragraph_text)
                data["paragraphs"].append(paragraph_text)
        
        for img in soup.find_all('img'):
            img_url = img.get('src')
            if img_url:
                full_img_url = urljoin(url, img_url)
                if full_img_url not in unique_images:
                    unique_images.add(full_img_url)
                    data["images"].append(full_img_url)
        
        for link in soup.find_all('a'):
            href = link.get('href')
            if href and not href.startswith('#'):
                full_url = urljoin(url, href)
                if full_url not in visited_urls:
                    data["links"].append(full_url)
                    scrape_url(full_url)
                    
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        
if __name__ == "__main__":
    base_url = f"http://{sys.argv[1]}"
    domain_name = urlparse(base_url).netloc

    visited_urls = set()
    unique_titles = set()  
    unique_paragraphs = set()  
    unique_images = set()  

    data = {
        "links": [],
        "titles": [],
        "paragraphs": [],
        "images": [],
        "meta": {},
        "social_media": {},
        "forms": [],
        "videos": []
    }

    try:
        scrape_url(base_url)
    except Exception as e:
        print(f"Genel hata oluştu: {e}")
    finally:
        save_data(data)  # Program sonlandırılmadan önce verileri kaydet