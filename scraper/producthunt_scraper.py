import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ProductHuntScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.ai_startups = []
        
    def setup_selenium(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        # Use ChromeDriverManager without version parameter
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
    
    def scrape_ai_products(self, num_products=25):
        """
        Scrape AI products from Product Hunt
        """
        self.setup_selenium()
        
        # Navigate to ProductHunt AI tools page
        self.driver.get("https://www.producthunt.com/topics/artificial-intelligence")
        
        # Wait for the page to load
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-test='product-item']"))
        )
        
        products = []
        scrolls = 0
        max_scrolls = 10  # Limit the number of scrolls
        
        while len(products) < num_products and scrolls < max_scrolls:
            print(f"Scroll {scrolls+1}/{max_scrolls}...")
            
            # Get all product items
            product_items = self.driver.find_elements(By.CSS_SELECTOR, "div[data-test='product-item']")
            
            for item in product_items:
                if len(products) >= num_products:
                    break
                
                try:
                    name = item.find_element(By.CSS_SELECTOR, "h3").text
                    
                    # Check if product is already in our list
                    if any(p["name"] == name for p in products):
                        continue
                    
                    description = item.find_element(By.CSS_SELECTOR, "p").text
                    
                    # Extract URL
                    try:
                        link = item.find_element(By.CSS_SELECTOR, "a")
                        product_url = "https://www.producthunt.com" + link.get_attribute("href")
                    except:
                        product_url = "N/A"
                    
                    # Extract upvote count
                    try:
                        upvotes = item.find_element(By.CSS_SELECTOR, "div[data-test='vote-button'] span").text
                    except:
                        upvotes = "0"
                    
                    products.append({
                        "name": name,
                        "description": description,
                        "product_url": product_url,
                        "upvotes": upvotes
                    })
                    
                    print(f"Scraped {name}")
                    
                except Exception as e:
                    print(f"Error scraping product: {e}")
            
            # Scroll down to load more products
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(2, 4))  # Random delay to avoid detection
            scrolls += 1
        
        self.ai_startups = products[:num_products]
        self.driver.quit()
        return self.ai_startups
    
    def scrape_product_details(self):
        """
        Scrape additional details for each product
        """
        self.setup_selenium()
        
        for i, product in enumerate(self.ai_startups):
            print(f"Scraping details for {product['name']} ({i+1}/{len(self.ai_startups)})")
            
            try:
                self.driver.get(product["product_url"])
                time.sleep(random.uniform(2, 4))  # Random delay
                
                # Extract website
                try:
                    website_btn = self.driver.find_element(By.XPATH, "//a[text()='Website']")
                    product["website"] = website_btn.get_attribute("href")
                except:
                    product["website"] = "N/A"
                
                # Extract pricing info
                try:
                    pricings = self.driver.find_elements(By.CSS_SELECTOR, "div.pricing span")
                    product["pricing"] = ", ".join([price.text for price in pricings])
                except:
                    product["pricing"] = "N/A"
                
                # Extract categories/tags
                try:
                    tags = self.driver.find_elements(By.CSS_SELECTOR, "a.topic")
                    product["categories"] = ", ".join([tag.text for tag in tags])
                except:
                    product["categories"] = "N/A"
                
                # Extract launch date
                try:
                    launch_date = self.driver.find_element(By.CSS_SELECTOR, "span.launched").text
                    product["launch_date"] = launch_date.replace("Launched ", "")
                except:
                    product["launch_date"] = "N/A"
                
            except Exception as e:
                print(f"Error scraping details for {product['name']}: {e}")
            
            # Be nice to the server
            time.sleep(random.uniform(1, 3))
        
        self.driver.quit()
        return self.ai_startups
    
    def save_to_csv(self, filename="ai_producthunt_data.csv"):
        """
        Save the scraped data to a CSV file
        """
        output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        df = pd.DataFrame(self.ai_startups)
        df.to_csv(output_path, index=False)
        print(f"Data saved to {output_path}")
        return output_path

if __name__ == "__main__":
    scraper = ProductHuntScraper()
    scraper.scrape_ai_products(25)
    scraper.scrape_product_details()
    scraper.save_to_csv()
