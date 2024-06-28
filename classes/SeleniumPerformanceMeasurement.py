from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService

from BasePerformanceMeasurement import BasePerformanceMeasurement

class SeleniumPerformanceMeasurement(BasePerformanceMeasurement):
    def __init__(self, url, driver):
        super().__init__(url)
        self.driver = driver


    @staticmethod
    def authenticate(site, driver):
        if 'authentication' not in site:
            return  # No authentication data present

        url = site['url']
        username = site['authentication']['username']
        password = site['authentication']['password']
        driver.get(url)

        # Update these selectors based on the actual login form
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "email")))
        username_field = driver.find_element(By.ID, "email")
        password_field = driver.find_element(By.ID, "password")
        username_field.send_keys(username)
        password_field.send_keys(password)

        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        WebDriverWait(driver, 10).until(EC.url_changes(url))


    @staticmethod
    def create_driver(config):
        print("Creating Selenium Driver")
        service = ChromeService(executable_path=config.get("driver_path", "/usr/local/bin/"))
        options = ChromeOptions()
        
        headless = config.get("headless", False)
        window_size = config.get("window_size", {"width": 1920, "height": 1080})
        options.add_argument(f"--headless={headless} --window-size={window_size['width']}x{window_size['height']}")

        return webdriver.Chrome(service=service, options=options)


    def measure_performance(self):
        print(f"Measuring performance for: {self.url}")
        self.driver.get(self.url)
        # Wait for the page to load completely
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Get performance metrics
        metrics = self.get_performance_metrics()

        # Logging metrics
        print(f"Performance metrics for {self.url}:")
        for key, value in metrics.items():
            print(f"{key}: {value}")


    @staticmethod
    def get_performance_metrics(driver):
        # JavaScript to extract performance metrics
        metrics_js = """
        var timing = performance.timing;
        var paint = performance.getEntriesByType('paint');
        var resources = performance.getEntriesByType('resource');
        var numberOfRequests = resources.length;
        var totalSize = 0;
        for (var resource of resources) {
            totalSize += resource.transferSize;
        }

        return {
            'loadTime': timing.loadEventEnd - timing.navigationStart,
            'firstPaint': paint.length > 0 ? paint[0].startTime : 0,
            'domContentLoaded': timing.domContentLoadedEventEnd - timing.navigationStart,
            'numberOfRequests': numberOfRequests,
            'pageWeightBytes': totalSize
        };
        """
        return driver.execute_script(metrics_js)