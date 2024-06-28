from BasePerformanceMeasurement import BasePerformanceMeasurement
import time
class RequestsPerformanceMeasurement(BasePerformanceMeasurement):
    def __init__(self, url, session):
        super().__init__(url)
        self.session = session
        self.response_code = None  # Initialise the response_code attribute

    def authenticate(site, session):
        if not site:
            raise ValueError("Site not defined")
        
        if not session:
            raise ValueError("Session not defined")
        
        username = site['authentication']['username']
        password = site['authentication']['password']
        login_data = {
            'username': username,
            'password': password
        }
        response = session.post(site['url'], data=login_data)

        # Check if the authentication was successful
        if response.status_code != 200:
            raise Exception("Authentication failed")
        

    def get_performance_metrics(self):
        metrics = {
            'loadTime': 0,
            'statusCode': 0,
            'firstPaint': 0,
            'domContentLoaded': 0,
            'numberRequests': 0,
            'pageWeightBytes': 0
        }
        return metrics


    def measure_performance(self, site, page_url):
        url = f"{site}{page_url}"
        response = self.session.get(url)
        response_code = response.status_code
        
        # Get elapsed time as seconds, round to 2 decimal places
        load_time_rounded = round(response.elapsed.total_seconds(), 2)

        metrics = self.get_performance_metrics()
        metrics['loadTime'] = load_time_rounded
        metrics['statusCode'] = response_code

        # Print metrics key and values
        print()
        print("Metrics:")
        for key, value in metrics.items():
            print(f"{key}: {value}")

        return metrics