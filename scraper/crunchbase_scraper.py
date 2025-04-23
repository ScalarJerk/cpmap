import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Load environment variables
load_dotenv()

class CrunchbaseScraper:
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
    
    def scrape_ai_startups(self, num_startups=25):
        """
        Scrape AI startups from Crunchbase
        """
        self.setup_selenium()
        
        # Navigate to Crunchbase AI startups page
        self.driver.get("https://www.crunchbase.com/discover/organization.companies/field/organizations/categories/artificial-intelligence")
        
        # Wait for the page to load
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "component--grid-row"))
        )
        
        startups = []
        page = 1
        
        while len(startups) < num_startups:
            print(f"Scraping page {page}...")
            
            # Get all startup rows
            rows = self.driver.find_elements(By.CLASS_NAME, "component--grid-row")
            
            for row in rows:
                if len(startups) >= num_startups:
                    break
                
                try:
                    name = row.find_element(By.CSS_SELECTOR, "a.link-primary").text
                    description = row.find_element(By.CSS_SELECTOR, "div.field-description").text
                    
                    # Extract funding info if available
                    try:
                        funding = row.find_element(By.CSS_SELECTOR, "div.field-funding_total").text
                    except:
                        funding = "N/A"
                    
                    # Extract location if available
                    try:
                        location = row.find_element(By.CSS_SELECTOR, "div.field-location_identifiers").text
                    except:
                        location = "N/A"
                    
                    profile_url = row.find_element(By.CSS_SELECTOR, "a.link-primary").get_attribute("href")
                    
                    startups.append({
                        "name": name,
                        "description": description,
                        "funding": funding,
                        "location": location,
                        "profile_url": profile_url
                    })
                    
                    print(f"Scraped {name}")
                    
                except Exception as e:
                    print(f"Error scraping row: {e}")
            
            if len(startups) < num_startups:
                try:
                    # Try to go to next page
                    next_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Next')]")
                    if next_button.is_enabled():
                        next_button.click()
                        page += 1
                        time.sleep(random.uniform(2, 4))  # Random delay to avoid detection
                    else:
                        break
                except:
                    break
        
        self.ai_startups = startups[:num_startups]
        self.driver.quit()
        return self.ai_startups
    
    def scrape_startup_details(self):
        """
        Scrape additional details for each startup
        """
        self.setup_selenium()
        
        for i, startup in enumerate(self.ai_startups):
            print(f"Scraping details for {startup['name']} ({i+1}/{len(self.ai_startups)})")
            
            try:
                self.driver.get(startup["profile_url"])
                time.sleep(random.uniform(2, 4))  # Random delay to avoid detection
                
                # Extract additional details
                try:
                    categories = self.driver.find_elements(By.CSS_SELECTOR, "div.category-list span.cb-text-color-medium-gray")
                    startup["categories"] = ", ".join([cat.text for cat in categories])
                except:
                    startup["categories"] = "N/A"
                
                # Extract website
                try:
                    website = self.driver.find_element(By.CSS_SELECTOR, "a.link-accent").get_attribute("href")
                    startup["website"] = website
                except:
                    startup["website"] = "N/A"
                
                # Extract founding date
                try:
                    founding_date = self.driver.find_element(By.XPATH, "//span[text()='Founded Date']/following-sibling::div").text
                    startup["founding_date"] = founding_date
                except:
                    startup["founding_date"] = "N/A"
                
                # Extract company size
                try:
                    company_size = self.driver.find_element(By.XPATH, "//span[text()='Number of Employees']/following-sibling::div").text
                    startup["company_size"] = company_size
                except:
                    startup["company_size"] = "N/A"
                
            except Exception as e:
                print(f"Error scraping details for {startup['name']}: {e}")
            
            # Be nice to the server
            time.sleep(random.uniform(1, 3))
        
        self.driver.quit()
        return self.ai_startups
    
    def save_to_csv(self, filename="ai_startups_data.csv"):
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
    scraper = CrunchbaseScraper()
    scraper.scrape_ai_startups(25)
    scraper.scrape_startup_details()
    scraper.save_to_csv()
