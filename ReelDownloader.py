from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import os
import shutil
import random
import time
import pandas as pd

# Setup Selenium WebDriver to use chrome with automatic download settings
def setup_selenium(download_folder):
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    chrome_options = Options()
    
    prefs = {
        "download.default_directory": os.path.abspath(download_folder),  # Set the download folder
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    }
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Set up Chrome driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    print("driver = ",driver)
    
    return driver

# Function to get the next available serialized filename
def get_next_serialized_filename(download_folder):
    existing_files = [f for f in os.listdir(download_folder) if f.startswith('Video_') and f.endswith('.mp4')]
    if existing_files:
        last_file = max(existing_files, key=lambda x: int(x.split('_')[1].split('.')[0]))
        next_index = int(last_file.split('_')[1].split('.')[0]) + 1
    else:
        next_index = 1
    return f"Video_{next_index}.mp4"

# Function to check if the download is complete
def is_download_complete(download_folder):
    temp_files = [f for f in os.listdir(download_folder) if f.endswith('.crdownload') or f.endswith('.tmp')]
    return len(temp_files) == 0

# Function to handle file renaming after download
def rename_downloaded_file(download_folder):
    # Wait until there are no active downloads
    while not is_download_complete(download_folder):
        time.sleep(5)  # Check every 5 seconds
    files = [f for f in os.listdir(download_folder) if f.endswith('.mp4')]
    # Generate a serialized filename
    new_filename = get_next_serialized_filename(download_folder)
    print("new_filename = ",new_filename)
    if files:
        latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(download_folder, x)))
        latest_file_path = os.path.join(download_folder, latest_file)
        new_file_path = os.path.join(download_folder, new_filename)
        shutil.move(latest_file_path, new_file_path)
        print(f"File renamed to: {new_filename}")

# Function to download Instagram reels using sssinstagram.net
def download_instagram_reels_sssinstagram(reel_url, download_folder):
    driver = setup_selenium(download_folder)
    # Navigate to sssinstagram's Instagram Reel Downloader
    driver.get("https://sssinstagram.com/reels-downloader")
    time.sleep(10)
    try:
        # Find the input box and paste the reel URL
        input_box = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//input[@id='input']"))
        )
        input_box.send_keys(reel_url)
        
        # Click the Download button to submit the URL
        download_button = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//button[@type='submit']"))
        )
        download_button.click()
        time.sleep(10)

    
        # Wait for either of the "Download Video" buttons to appear and get the href
        download_video_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[@class='button button--filled button__download']"))
        )

        # Extract the href link for the video
        video_download_link = download_video_button.get_attribute("href")
        print(f"Download link: {video_download_link}")
        
        # Download the video manually using the extracted href link
        driver.get(video_download_link)
        time.sleep(10)  # Give time for the download to start
        
        # Rename the file after download
        rename_downloaded_file(download_folder)

        # print(f"Download attempt finished for: {reel_url}")
        driver.quit() 
        return 1
        
    except Exception as e:
        print(f"Error clicking the download button or fetching video link: {str(e)}")
        driver.quit() 
        return 0
    
# Add this function to handle retries
def download_with_retry(reel_url, download_folder, max_retries=7):
    attempt = 0
    success = False

    while attempt < max_retries and not success:
        print("attempt Reel= ",attempt)
        number = download_instagram_reels_sssinstagram(reel_url, download_folder)
        if number == 1:
            success = True
            break
        else:
            attempt += 1
            time.sleep(5)  # Wait for a few seconds before retrying
            
    if not success:
        print(f"Failed to download reel after {max_retries} attempts: {reel_url}")
                  
# Main function to automate the process
def main():
    
    # STEP 1
    
    download_folder = "VIDEOS"  # Set this to your desired download folder
    
    # Read only the first 50 reel links from the .txt file and remove them after processing
    input_file = 'ordered_reel_links_copy.txt'
    with open(input_file, 'r') as file:
        lines = file.readlines()

    first_5 = [line.strip() for line in lines[:5]]
    remaining = lines[5:]

    # Write back the remaining links to the file
    with open(input_file, 'w') as file:
        file.writelines(remaining)

    # Download reels for the first 50 links
    for reel_link in first_5:
        if reel_link:  # skip empty lines
            download_with_retry(reel_link, download_folder)

if __name__ == "__main__":
    main()
