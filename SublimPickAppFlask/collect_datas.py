from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from google.cloud import storage  # Import the Google Cloud Storage client
import pandas as pd
import os
import time

from basic_functions import (
    collect_urls,
    collect_reviews,
    save_urls_to_gcs,
    save_reviews_to_gcs
)

# Get the current month (integer)
def get_current_month():
    return time.strftime("%m")

def main():
    # List of product listing URLs to scrape
    urls = ["https://www.dermstore.com/skin-care.list",
            "https://www.dermstore.com/hair-care.list",
            "https://www.dermstore.com/makeup.list"]

    # Setup Selenium with Chrome options
    PATH = Service(os.path.join(os.curdir, 'chromedriver.exe'))
    OPTIONS = Options()

    # User agent
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36'
    OPTIONS.add_argument(f'user-agent={user_agent}')

    # Disable unnecessary functionality causing message error in the console
    OPTIONS.add_argument("--disable-extensions --disable-gpu --disable-dev-shm-usage --disable")
    OPTIONS.add_experimental_option('excludeSwitches', ['enable-logging'])

    # Closing some unnecessary pop-ups
    OPTIONS.add_argument("--no-first-run --no-service-autorun --password-store=basic")

    # Start in full-screen with a defined window size
    OPTIONS.add_argument("window-size=1920,1080")
    OPTIONS.add_argument("start-maximised")

    # Hide some bot related stuff to increase stealthiness
    OPTIONS.add_argument('--disable-blink-features=AutomationControlled')
    OPTIONS.add_experimental_option('useAutomationExtension', False)
    OPTIONS.add_experimental_option("excludeSwitches", ['enable-automation'])

    # Headless
    OPTIONS.add_argument("--headless")
    
    driver = webdriver.Chrome(service=PATH, options=OPTIONS)

    # Collect product URLs
    products_list = collect_urls(driver, urls)

    print("[LOG] Collecting reviews ...")
    # Collect reviews for the URLs
    reviews = collect_reviews(driver, products_list)

    # Create DataFrame from reviews
    df = pd.DataFrame([item for sublist in reviews for item in sublist],
                      columns=['review_url_src', 'review_stars', 'review_title', 'review_thoughts',
                               'review_author', 'review_date', 'review_verified', 'review_tup',
                               'review_tdown', 'review_collected_date'])

    # Get the current month for GCS folder structure
    current_month = get_current_month()

    # Save URLs to Google Cloud Storage
    save_urls_to_gcs(products_list, current_month)

    # Save reviews to Google Cloud Storage
    save_reviews_to_gcs(df, current_month)

if __name__ == "__main__":
    main()
