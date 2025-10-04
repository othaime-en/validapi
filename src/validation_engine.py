from typing import Dict, Any, List, Optional
from pathlib import Path
import requests
from parsers.openapi_parser import OpenAPIParser
from validators.schema_validator import SchemaValidator, StatusCodeValidator, HeaderValidator
from utils.http_client import HTTPClient
from config.settings import settings

class ValidationEngine:
    
    def __init__(self, spec_path: str, base_url: Optional[str] = None):
        self.parser = OpenAPIParser(spec_path)
        self.base_url = base_url or self.parser.base_url
        self.client = HTTPClient(self.base_url)
        
        # Initialize validators
        self.validators = {
            'schema': SchemaValidator(),
            'status_code': StatusCodeValidator(),
            'header': HeaderValidator()
        }
        
        self.results = []
    
    def validate_endpoint(self, path: str, method: str, test_data: Optional[Dict] = None) -> Dict[str, Any]:
        # We validate a single endpoint
        pass


    def validate_all_endpoints(self, test_data: Optional[Dict] = None) -> List[Dict[str, Any]]:
        # Validate all endpoints in the specification
        pass

    
    def _make_request(self, path: str, method: str, test_data: Optional[Dict] = None) -> requests.Response:
        # Make a HTTP request to an endpoint"""
        
        # Prepare request parameters
        params = {}
        json_data = None
        headers = {}
        
        if test_data:
            params = test_data.get('params', {})
            json_data = test_data.get('json', None)
            headers = test_data.get('headers', {})
        
        return self.client.request(
            method=method,
            endpoint=path,
            params=params,
            json=json_data,
            headers=headers
        )
    
    def _validate_response(self, response: requests.Response, endpoint_info: Dict[str, Any]) -> Dict[str, Any]:
        # Here, we will validate the response against specification
        pass
