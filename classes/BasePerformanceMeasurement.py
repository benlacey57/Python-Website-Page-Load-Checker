class BasePerformanceMeasurement:
    def __init__(self, url):
        self.url = url

    def authenticate(self):
        raise NotImplementedError("Subclasses should implement the authenticate method")
    
    def measure_performance(self):
        raise NotImplementedError("Subclasses should implement the measure_performance method")

    def get_performance_metrics(self):
        raise NotImplementedError("Subclasses should implement the get_performance_metrics method")