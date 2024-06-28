import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import sys
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Check if the script is run as root (on Unix-based systems)
if os.geteuid() == 0:
    print("Error: Please run this script as your standard user, not as root.")
    sys.exit(1)

# Get the parent folder where the script is run
script_root = os.path.abspath(os.path.dirname(__file__))

# Load environment variables from .env file at the project root
# env_path = os.path.join(script_root, '.env')
# load_dotenv(dotenv_path=env_path)

# Access the passwords from environment variables
# staging_password = os.getenv('STAGING_PASSWORD')
# production_password = os.getenv('PRODUCTION_PASSWORD')

# Load configuration from config.json
config_path = os.path.join(script_root, 'config.json')
with open(config_path, 'r') as file:
    config = json.load(file)

# Update the configuration with the passwords from the environment variables
# config['sites']['production']['authentication']['password'] = production_password
# config['sites']['staging']['authentication']['password'] = staging_password

options = Options()
options.add_argument('--headless')
options.add_argument("--window-size=1920,1080")

# Function to get performance metrics
def get_performance_metrics(driver):
    metrics_js = """
        const timing = window.performance.timing;
        const paint = window.performance.getEntriesByType('paint');
        const resources = window.performance.getEntriesByType('resource');

        let numberOfRequests = resources.length;
        let totalSize = 0;
        for (let resource of resources) {
            totalSize += resource.transferSize;
        }

        return {
            'loadTime': (timing.loadEventEnd - timing.navigationStart) / 1000,
            'firstPaint': (paint.length > 0 ? paint[0].startTime : 0) / 1000,
            'domContentLoaded': (timing.domContentLoadedEventEnd - timing.navigationStart) / 1000,
            'numberRequests': numberOfRequests,
            'pageWeightBytes': totalSize
        };
    """
    return driver.execute_script(metrics_js)

# Create argument parser
parser = argparse.ArgumentParser()
parser.add_argument('--note', help='Specify a note for the test')
args = parser.parse_args()

# Set the filename based on the note
if args.note:
    note = args.note
    csv_file = f'{script_root}/data/selenium_automated_tests.csv'
else:
    # Prompt for a note if not passed as an argument
    note = input("Enter a note: ") or "Manual Test"
    csv_file = f'{script_root}/data/selenium_manual_tests.csv'

# Iterate over each site in the config
for site_key, site in config['sites'].items():
    if not site['enabled']:
        continue
    
    driver = webdriver.Chrome(options=options)
    print(f"\nSpeed Checking Site: {site['url']}\n")

    # Perform authentication if credentials are available
    if 'authentication' in site:
        print('Authenticating...')
        driver.get(site['url'])
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "email")))
        username_field = driver.find_element(By.ID, "email")
        password_field = driver.find_element(By.ID, "password")
        username_field.send_keys(site['authentication']['username'])
        password_field.send_keys(site['authentication']['password'])
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        WebDriverWait(driver, 20).until(EC.url_changes(site['url']))

    # Save the load time to a CSV file
    write_header = not os.path.exists(csv_file)

    with open(csv_file, 'a') as file:
        if write_header:
            headers = [
                'Timestamp',
                'Site URL',
                'Page Name',
                'Page URL',
                'Load Time',
                'First Paint',
                'DOM Content Loaded',
                'Number Requests',
                'Page Weight Bytes',
                'Measurement Method',
                'Note'
            ]
            file.write(','.join(headers) + '\n')

        # Iterate over each page in the config
        for page in config['pages']:
            site_url = site['url']
            page_url = page['url']
            full_url = site_url + page_url
            page_name = page['name']
            start_time = time.time()

            driver.get(full_url)
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            metrics = get_performance_metrics(driver)
            metrics['loadTime'] = round(time.time() - start_time, 2)
            metrics['firstPaint'] = round(metrics['firstPaint'], 2)
            metrics['domContentLoaded'] = round(metrics['domContentLoaded'], 2)
            metrics['pageWeightBytes'] = round(metrics['pageWeightBytes'] / 1000000, 2)

            load_time = metrics['loadTime']
            target_load_time = config['target_load_time']

            if load_time > target_load_time:
                print(f'\033[91m{page["name"]} Page - Load Time: {load_time:.2f} seconds (SLOW)\033[0m')
            else:
                print(f'\033[92m{page["name"]} Page - Load Time: {load_time:.2f} seconds (OK)\033[0m')

            row = [
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                site_url,
                page_name,
                full_url,
                metrics.get('loadTime', ''),
                metrics.get('firstPaint', ''),
                metrics.get('domContentLoaded', ''),
                metrics.get('numberRequests', ''),
                metrics.get('pageWeightBytes', ''),
                "Selenium",
                note
            ]
            file.write(','.join(map(str, row)) + '\n')
            file.flush()

    driver.quit()
