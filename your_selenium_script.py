from selenium import webdriver
from selenium.webdriver.chrome.service import Service

# Use default chromedriver path
service = Service('/usr/local/bin/chromedriver')
driver = webdriver.Chrome(service=service)

# Add your Selenium script logic here
# Example:
driver.get("https://www.example.com")
print(driver.title)

driver.quit()