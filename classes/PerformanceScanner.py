from datetime import datetime
import json
import logging
import os
import re
import requests

from RequestsPerformanceMeasurement import RequestsPerformanceMeasurement
from SeleniumPerformanceMeasurement import SeleniumPerformanceMeasurement

class PerformanceScanner:
    config = None
    report_timestamp = None
    pages = None
    session = None
    note = None
    script_root = None
    selenium_driver = None

    def __init__(self, script_root, note):
        self.script_root = script_root
        self.note = note
        self.config = self.read_config()
        self.report_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        self.logger = self.setup_global_logger()
        self.welcome_banner()

        self.selenium_driver = None
        self.requests_session = requests.Session()

        measurement_method = self.config.get("speed_check_method", "selenium")
        for site in self.config.get("sites", []):
            self.setup_folders(site)
            self.run_speed_check(site, measurement_method)

        if self.selenium_driver:
            self.selenium_driver.quit()
    

    # Print the welcome banner to the console
    def welcome_banner(self):
        self.clear_console()
        print('-' * 30)
        print('  Website Performance Scanner  ')
        print('-' * 30)
        print(f'\nThis script will run a speed test on the pages defined in config.json')

        target_load_time = self.config.get("target_load_time", 3)
        print(f'Target Load Time: {target_load_time} seconds\n')

        print('Pages to be tested:\n')
        for page in self.config.get("pages", []):
            print(f'- {page["name"]} Page ({page["url"]})')
        print('\n')


    def clear_console(self):
        os.system('cls' if os.name == 'nt' else 'clear')


    # Create folders for each site if they don't already exist
    def setup_folders(self, site):
        self.logger.info('> Setting up domain folders')
        domain_folder = self.get_domain_folder(site)
        
        # Create the folders if they don't exist
        if not os.path.exists(f'data/{domain_folder}'):
            folders = [
                'data',
                'logs',
                'reports',
                f'data/{domain_folder}',
                f'data/{domain_folder}/lighthouse',
                f'data/{domain_folder}/gtmetrix',
                f'reports/{domain_folder}'
            ]

            for folder in folders:
                if not os.path.exists(folder):
                    os.makedirs(folder)

            folder_count = len(folders)
            self.logger.info(f'Created {folder_count} folders for {domain_folder}')
        else:
            self.logger.info(f'Folders already exist for {domain_folder}')


    def get_domain_folder(self, site):
        self.logger.info('> Extracting domain folder from URL')
        site_url = site['url']

        # Get the domain folder name for the site
        match = re.search(r'(?<=://)(.*?)(?=/|$)', site["url"])
        if match:
            domain_folder = match.group(0)
            self.logger.info(f'Extracted Folder: {domain_folder}')
            
            return domain_folder
        
        else:
            # Handle the case where the regular expression doesn't match
            self.logger.error(f'Failed to extract folder name: {site_url}')
            return None

    def read_config(self):
        config_path = os.path.join(self.script_root, 'config.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config


    def setup_global_logger(self):
        logger = logging.getLogger('PerformanceScanner')  # Use getLogger from the logging module
        logger.setLevel(logging.INFO)

        if not os.path.exists('logs'):
            os.makedirs('logs')

        file_handler = logging.FileHandler(os.path.join(self.script_root, 'logs', 'performance_scanner.log'))
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger


    def summary(self):
        print('')
        print('-' * 25)
        print('Speed Test Report Summary')
        print('-' * 25)

        for site in self.config.get("sites", []):
            self.logAndPrint(f'Site: {site["url"]}', 'info')

            for page in self.config.get("pages", []):
                url = f'{site["url"]}{page["url"]}'
                page_name = page["name"]
                target_load_time = self.config.get("target_load_time", 3)

                # Read data from the consolidated CSV file
                domain_folder = self.get_domain_folder(site)
                csv_path = f'{self.script_root}/data/{domain_folder}/speed_check.csv'
                slow_pages = 0

                if os.path.exists(csv_path):
                    with open(csv_path, 'r') as f:
                        lines = f.readlines()[1:]  # Skip the header row
                        for line in lines:
                            page_name_csv, load_time = line.strip().split(',')
                            load_time = float(load_time)

                            if page_name_csv == page_name:
                                if load_time > target_load_time:
                                    print(f'\033[91m{page_name} Page ({url}) - Load Time: {load_time:.2f} seconds\033[0m', 'info')
                                    self.logger.error(f'{page_name} Page ({url}) - Load Time: {load_time:.2f} seconds (SLOW)')
                                    slow_pages += 1
                                else:
                                    print(f'\033[92m{page_name} Page ({url}) - Load Time: {load_time:.2f} seconds\033[0m')
                                    self.logger.success(f'{page_name} Page ({url}) - Load Time: {load_time:.2f} seconds (OK)')
                                

            if slow_pages > 0:
                self.logAndPrint(f'Slow Pages: {slow_pages} (Longer than {target_load_time} seconds)', 'error')
            else:
                self.logAndPrint(f'All pages meet the target load time ({target_load_time} seconds)', 'success')


    def create_measurement(self, measurement_method, site, page_url):
        # Create and return the appropriate measurement object
        url = f'{site["url"]}{page_url}'
        
        if measurement_method == 'requests':
            print('Using Requests')
            return RequestsPerformanceMeasurement(url, self.requests_session)
        elif measurement_method == 'selenium':
            if not self.selenium_driver:
                selenium_config = self.config.get("selenium", {})
                self.selenium_driver = SeleniumPerformanceMeasurement.create_driver(selenium_config)
            return SeleniumPerformanceMeasurement(url, self.selenium_driver)
        else:
            raise ValueError(f"Unknown measurement method: {measurement_method}")


    # Run speed check on the pages and store the information in a CSV file with the timestamp (appending for each run)
    def run_speed_check(self, site, measurement_method):
        self.logger.info(f'Running Speed Check for {site["url"]}')
        print(f'\nRunning Speed Check for {site["url"]}\n')

        domain_folder = self.get_domain_folder(site)
        csv_file = f'{self.script_root}/data/{domain_folder}/speed_check.csv'
        write_header = not os.path.exists(csv_file)

        # Perform authentication if necessary
        if "authentication" in site:            
            if measurement_method == 'selenium':
                driver = SeleniumPerformanceMeasurement.create_driver(self.config.get("selenium", {}))
                SeleniumPerformanceMeasurement.authenticate(site=site, driver=driver)
            elif measurement_method == 'requests':
                RequestsPerformanceMeasurement.authenticate(site=site, session=self.requests_session)

        # Save the load time to a CSV file
        with open(csv_file, 'a') as file:
            if write_header:
                headers = [
                    'Timestamp', 
                    'Page URL', 
                    'Page Name', 
                    'Load Time', 
                    'Status Code',
                    'First Paint', 
                    'DOM Content Loaded', 
                    'Number Requests',
                    'Page Weight Bytes', 
                    'Measurement Method', 
                    'Note'
                ]
                file.write(','.join(headers) + '\n')

            for page in self.config.get("pages", []):
                self.logger.info(f'Running Speed Check for {page["name"]} Page')   
                url = f'{site["url"]}{page["url"]}'
                target_load_time = self.config.get("target_load_time", 3)

                measurement = self.create_measurement(measurement_method=measurement_method, site=site, page_url=page['url'])
                metrics = measurement.measure_performance(site=site, page_url=page['url'])
                load_time = metrics.get('loadTime')

                if load_time > target_load_time:
                    print(f'\033[91m{page["name"]} Page - Load Time: {load_time:.2f} seconds (SLOW)\033[0m')
                    self.logger.error(f'{page["name"]} Page - Load Time: {load_time:.2f} seconds (SLOW)')
                else:
                    print(f'\033[92m{page["name"]} Page - Load Time: {load_time:.2f} seconds (OK)\033[0m')
                    self.logger.info(f'{page["name"]} Page - Load Time: {load_time:.2f} seconds (OK)')

                row = [
                    self.report_timestamp, 
                    f'{url}', 
                    page["name"],
                    metrics.get('loadTime', ''), 
                    metrics.get('statusCode', ''),
                    metrics.get('firstPaint', ''), 
                    metrics.get('domContentLoaded', ''),
                    metrics.get('numberRequests', ''), 
                    metrics.get('pageWeightBytes', ''),
                    measurement_method, 
                    self.note
                ]
                file.write(','.join(map(str, row)) + '\n')

                self.logger.info('CSV File Updated Successfully')

        # Quit the Selenium driver after processing all pages if using Selenium
        if self.selenium_driver:
            self.selenium_driver.quit()

        print("")
        

    def run_lighthouse_checks(self, site):
        domain_folder = self.get_domain_folder(site)
        site_url = site['url']

        self.logger.info(f'Running Lighthouse checks for {site_url}')

        if not self.config.get("pages"):
            self.logAndPrint(f'Cannot perform Lighthouse scan - No pages specified in the config.json for {site}', 'error')
            return

        for page in self.config["pages"]:
            # Run Lighthouse scan for each page using the authenticated session
            url = self.session.get(f'{site}{page["url"]}')


    def process_lighthouse_report(self, lighthouse_result_file, site):
        print('')
        self.logAndPrint('> Processing Lighthouse Report', 'info')
        domain_folder = self.get_domain_folder(site)

        # with pdfplumber.open(lighthouse_result_file) as pdf:
        #     full_text = ''
        #     for page in pdf.pages:
        #         full_text += page.extract_text()

        #     # Extract and process relevant information from full_text
        #     self.logAndPrint('> Running Lighthouse Checks', 'info')

        #     # Save as JSON
        #     extracted_data = {}  # Extracted data processing logic
        #     with open(f'data/{domain_folder}/lighthouse/extracted_metrics.json', 'w') as f:
        #         json.dump(extracted_data, f, indent=4)


    def logAndPrint(self, message, level):
        if level == 'error':
            self.logger.error(message)
        elif level == 'warning':
            self.logger.warning(message)
        elif level == 'success':
            self.logger.success(message)
        else:
            self.logger.info(message)
        
        print(message)
