import requests
from urllib.parse import urljoin
from src.config.settings import settings

class HTTPClient:
    """HTTP client for making API requests"""
    
    def __init__(self, base_url, headers):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
        # Set default headers from config
        # Configure session settings
        # Timeout settings
    
    def request(self, method, endpoint) -> requests.Response:
        """
        HTTP request
        """
        
        # Prepare request arguments        
        # Add retry logic later
        
    
    def get(self, endpoint) -> requests.Response:
        """
        GET request
        """
    
    def post(self, endpoint) -> requests.Response:
        """
        POST request
        """