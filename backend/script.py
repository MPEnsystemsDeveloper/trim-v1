import os
import time
import pandas as pd
import requests
from dotenv import load_dotenv

# Selenium Imports
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager

# --- Configuration & Environment Variables ---
load_dotenv()

BASE_URL = os.getenv("BASE_URL")
EMAIL = os.getenv("FLOCK_USERNAME")
PASSWORD = os.getenv("FLOCK_PASSWORD")
DEVICE_NAME = os.getenv("DEVICE_NAME")
DEVICE_ID = os.getenv("DEVICE_ID")

# --- Constants & Locators (for easy maintenance) ---
# Login Page
LOGIN_EMAIL_ID = "email"
LOGIN_PASSWORD_ID = "password"
LOGIN_BUTTON_XPATH = "//button[contains(text(), 'Sign in') or contains(text(), 'SIGN IN')]"

# Dashboard Page
DASHBOARD_HEADER_XPATH = "//h2[contains(text(), 'Device Fleet')]"
DEVICE_NAME_FILTER_XPATH = "//input[contains(@placeholder, 'Name')]"
DEVICE_ID_FILTER_XPATH = "//input[contains(@placeholder, 'ID')]"
APPLY_FILTER_BUTTON_XPATH = "//button[contains(text(), 'Apply Filter')]"
DEVICE_TABLE_CELL_XPATH = f"//td[contains(text(), '{DEVICE_NAME}')]"

# Device Details Page
DATA_FILTER_HEADER_XPATH = "//h2[contains(text(), 'Filter Data')]"
YESTERDAY_BUTTON_XPATH = "//button[text()='Yesterday']" 
# --- CORRECTED LOCATOR ---
# The resolution is also a button, so we target it directly by its text.
RAW_BUTTON_XPATH = "//button[text()='Raw']"
APPLY_DATA_FILTERS_BUTTON_XPATH = "//button[contains(text(), 'Apply Filters')]"
DOWNLOAD_CSV_BUTTON_XPATH = "//h2[contains(text(), 'Sensor Data')]/following::button[contains(text(), 'Download CSV')]"

# --- Main Script ---

# Setup
DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)
options = ChromeOptions()
options.headless = False
prefs = {"download.default_directory": DOWNLOAD_DIR}
options.add_experimental_option("prefs", prefs)
service = ChromeService(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    # Steps 1-5 (Login, Filter, Navigate to Device)
    print("[INFO] Starting the automation process...")
    driver.get(BASE_URL)
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, LOGIN_EMAIL_ID))).send_keys(EMAIL)
    driver.find_element(By.ID, LOGIN_PASSWORD_ID).send_keys(PASSWORD)
    driver.find_element(By.XPATH, LOGIN_BUTTON_XPATH).click()
    print("[INFO] Login submitted.")
    print("[INFO] Waiting up to 25s for dashboard to load...")
    WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.XPATH, DASHBOARD_HEADER_XPATH)))
    print("[INFO] Dashboard loaded successfully.")
    print(f"[INFO] Filtering for device: {DEVICE_NAME} ({DEVICE_ID})")
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, DEVICE_NAME_FILTER_XPATH))).send_keys(DEVICE_NAME)
    driver.find_element(By.XPATH, DEVICE_ID_FILTER_XPATH).send_keys(DEVICE_ID)
    driver.find_element(By.XPATH, APPLY_FILTER_BUTTON_XPATH).click()
    WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, DEVICE_TABLE_CELL_XPATH))).click()
    print("[INFO] Navigated to device details. Waiting up to 25s for data filter section to appear...")
    WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.XPATH, DATA_FILTER_HEADER_XPATH)))
    print("[INFO] Device details page loaded.")

    # Step 6: Click the "Yesterday" button
    print("[INFO] Waiting for the 'Yesterday' button to be clickable...")
    WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, YESTERDAY_BUTTON_XPATH))).click()
    print("[INFO] Timeframe set to 'Yesterday'.")

    # --- CORRECTED ACTION FOR RESOLUTION ---
    # Step 7: Click the "Raw" button for resolution
    print("[INFO] Waiting for the 'Raw' resolution button to be clickable...")
    WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, RAW_BUTTON_XPATH))).click()
    print("[INFO] Resolution set to 'Raw'.")

    # Step 8: Apply the data filters
    driver.find_element(By.XPATH, APPLY_DATA_FILTERS_BUTTON_XPATH).click()
    print("[INFO] Data filters applied.")

    # Step 9: Wait for the download button to be ready
    print("[INFO] Waiting up to 25s for sensor data and download button to render...")
    download_button = WebDriverWait(driver, 25).until(EC.element_to_be_clickable((By.XPATH, DOWNLOAD_CSV_BUTTON_XPATH)))
    print("[INFO] Download button is ready.")

    # Step 10: Download the CSV file
    csv_url = download_button.get_attribute("href")
    output_filename = "sensor_data.csv"

    if csv_url and 'javascript:void(0)' not in csv_url:
        print(f"[INFO] Direct CSV URL found. Downloading via requests session...")
        session = requests.Session()
        for cookie in driver.get_cookies():
            session.cookies.set(cookie['name'], cookie['value'])
        response = session.get(csv_url)
        if response.status_code == 200:
            with open(output_filename, "wb") as f:
                f.write(response.content)
            print(f"[SUCCESS] CSV downloaded as '{output_filename}'.")
        else:
            print(f"[ERROR] Failed to download CSV via URL. Status: {response.status_code}")
    else:
        print("[WARNING] No direct URL found. Using browser download fallback.")
        download_button.click()
        
        timeout = 45
        start_time = time.time()
        download_path = None
        while time.time() - start_time < timeout:
            files = [f for f in os.listdir(DOWNLOAD_DIR) if f.endswith('.csv') and not f.endswith('.crdownload')]
            if files:
                downloaded_file = os.path.join(DOWNLOAD_DIR, files[0])
                print(f"[SUCCESS] Browser download detected: {downloaded_file}")
                if os.path.exists(output_filename):
                    os.remove(output_filename)
                os.rename(downloaded_file, output_filename)
                print(f"[INFO] File renamed to '{output_filename}'.")
                download_path = output_filename
                break
            time.sleep(1)
        
        if not download_path:
             print(f"[ERROR] Download did not complete within {timeout} seconds.")

    # Step 11: Read the data with pandas
    if os.path.exists(output_filename):
        print("\n--- First 5 rows of the downloaded data ---")
        df = pd.read_csv(output_filename)
        print(df.head())
        print("-----------------------------------------")

finally:
    print("[INFO] Automation complete. Closing the browser.")
    driver.quit()