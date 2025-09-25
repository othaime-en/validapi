import requests
from typing import Dict, Any, Optional, Union
from urllib.parse import urljoin
from src.config.settings import settings

class HTTPClient:
    """HTTP client for making API requests"""
    
    def __init__(self, base_url: str = "", headers: Optional[Dict[str, str]] = None):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
        # Set default headers from config
        default_headers = settings.get('http.headers', {})
        if headers:
            default_headers.update(headers)
        self.session.headers.update(default_headers)
        
        # Configure session settings
        self.session.verify = settings.get('http.verify_ssl', True)
        
        # Timeout settings
        self.timeout = (
            settings.get('http.connection_timeout', 10),
            settings.get('http.read_timeout', 30)
        )
        
        self.max_retries = settings.get('validation.max_retries', 3)
    
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