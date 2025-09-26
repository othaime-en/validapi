import requests
import time
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
    
    def request(self, 
                method: str, 
                endpoint: str, 
                params: Optional[Dict] = None,
                data: Optional[Union[Dict, str]] = None,
                json: Optional[Dict] = None,
                headers: Optional[Dict] = None) -> requests.Response:
              
        """Make an HTTP request with retries"""
        url = urljoin(f"{self.base_url}/", endpoint.lstrip('/'))
        
        # Prepare request arguments
        request_args = {
            'method': method,
            'url': url,
            'timeout': self.timeout
        }
        
        if params:
            request_args['params'] = params
        if data:
            request_args['data'] = data
        if json:
            request_args['json'] = json
        if headers:
            request_args['headers'] = headers
        
        # Retry logic
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.request(**request_args)
                return response
                
            except requests.RequestException as e:
                last_exception = e
                if attempt == self.max_retries:
                    raise e
                
                # Wait before retrying (exponential backoff)
                wait_time = 2 ** attempt
                time.sleep(wait_time)
        
        # This should never be reached, but just in case
        if last_exception:
            raise last_exception
    
          
    
    def get(self, endpoint: str, **kwargs) -> requests.Response:
        """Make GET request"""
        return self.request('GET', endpoint, **kwargs)
    
    def post(self, endpoint: str, **kwargs) -> requests.Response:
        """Make POST request"""
        return self.request('POST', endpoint, **kwargs)
    
    def put(self, endpoint: str, **kwargs) -> requests.Response:
        """Make PUT request"""
        return self.request('PUT', endpoint, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """Make DELETE request"""
        return self.request('DELETE', endpoint, **kwargs)
    
    def patch(self, endpoint: str, **kwargs) -> requests.Response:
        """Make PATCH request"""
        return self.request('PATCH', endpoint, **kwargs)