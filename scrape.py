from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse, urljoin
import time

class WebsiteScraper:
    def __init__(self, base_url, max_depth=2, max_pages=50):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.visited_urls = set()
        self.data_structure = {}
        self.max_depth = max_depth  # How many link levels to follow
        self.max_pages = max_pages  # Maximum pages to scrape
        self.page_count = 0

        # Selenium setup
        service = Service()
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(service=service, options=options)
    
    def scrape_website(self):
        """Main scraping method"""
        self._scrape_page(self.base_url, depth=0)
        self._save_data()
        self.driver.quit()
        print(f"Scraping complete. Saved {self.page_count} pages.")
    
    def _scrape_page(self, url, depth):
        """Scrape an individual page"""
        if (url in self.visited_urls or 
            self.page_count >= self.max_pages or 
            depth > self.max_depth):
            return
            
        self.visited_urls.add(url)
        self.page_count += 1
        
        print(f"Scraping ({depth}): {url}")
        self.driver.get(url)
        time.sleep(2)  # Wait for page load
        
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['header', 'footer', 'nav', 'script', 'style', 'iframe', 'img']):
            element.decompose()
        
        # Extract all text content
        page_title = soup.title.string if soup.title else url
        main_content = soup.find('main') or soup.find('article') or soup.find('body')
        text_content = self._clean_text(main_content.get_text(separator=' ', strip=True))
        
        # Store page data
        page_key = self._url_to_key(url)
        self.data_structure[page_key] = {
            "url": url,
            "title": page_title,
            "content": text_content,
            "depth": depth,
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Find and follow internal links
        if depth < self.max_depth:
            for link in soup.find_all('a', href=True):
                href = link['href']
                if self._is_internal_link(href):
                    absolute_url = urljoin(self.base_url, href)
                    if absolute_url not in self.visited_urls:
                        self._scrape_page(absolute_url, depth + 1)
    
    def _clean_text(self, text):
        """Clean and normalize text"""
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        return ' '.join(chunk for chunk in chunks if chunk)
    
    def _is_internal_link(self, href):
        """Check if link belongs to same domain"""
        parsed = urlparse(href)
        return (not parsed.netloc or parsed.netloc == self.domain) and not href.startswith(('mailto:', 'tel:', '#'))
    
    def _url_to_key(self, url):
        """Convert URL to safe key"""
        parsed = urlparse(url)
        path = parsed.path.replace('/', '_').strip('_') or 'home'
        return f"{parsed.netloc}_{path}"[:100]
    
    def _save_data(self):
        """Save scraped data to JSON"""
        with open("scraped_website.json", "w", encoding="utf-8") as f:
            json.dump(self.data_structure, f, indent=2, ensure_ascii=False)

# Usage
if __name__ == "__main__":
    scraper = WebsiteScraper(
        base_url="https://lomitacity.com/",
        max_depth=5,    # How many link levels to follow
        max_pages=100   # Maximum pages to scrape
    )
    scraper.scrape_website()