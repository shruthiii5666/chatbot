from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time
import random

# Initialize Chrome driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Navigate to website
driver.get("https://lomitacity.com/#")

# Wait for page to load
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.TAG_NAME, 'body'))
)

# Find all navigation links (adjust selector based on actual page structure)
nav_links = driver.find_elements(By.CSS_SELECTOR, 'header nav a')

# Collect valid internal links
base_url = "https://lomitacity.com/"
critical_pages = set()

for link in nav_links:
    href = link.get_attribute('href')
    if href and href.startswith(base_url):
        critical_pages.add(href)

# Convert to list and select 50%
critical_pages = list(critical_pages)
selected_pages = critical_pages[:len(critical_pages)//2]

# Prepare CSV file
with open('raw_html_1.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['URL', 'Raw HTML'])
    
    # Scrape selected pages
    for url in selected_pages:
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(  # FIXED LINE
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )
            
            # Get page HTML
            page_html = driver.page_source
            writer.writerow([url, page_html])
            print(f"Scraped: {url}")
            
            # Respectful delay between requests
            time.sleep(random.uniform(1, 3))
            
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")

# Clean up
driver.quit()
print("Scraping completed. Data saved to raw_html_1.csv")