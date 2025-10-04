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
        
        # Replace path parameters
        final_path = self._replace_path_parameters(path, test_data)
        
        return self.client.request(
            method=method,
            endpoint=final_path,
            params=params,
            json=json_data,
            headers=headers
        )
    
    def _replace_path_parameters(self, path: str, test_data: Optional[Dict] = None) -> str:
        """Replace path parameters with test values"""
        if not test_data or 'path_params' not in test_data:
            return path
        
        final_path = path
        for param_name, param_value in test_data['path_params'].items():
            final_path = final_path.replace(f'{{{param_name}}}', str(param_value))
        
        return final_path
    
    
    def _validate_response(self, response: requests.Response, endpoint_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate response against specification"""
        validations = {}
        
        # Get expected status codes
        expected_codes = self.parser.get_expected_status_codes(
            endpoint_info['path'], 
            endpoint_info['method']
        )
        
        # Status code validation
        status_result = self.validators['status_code'].validate(
            response, {}, expected_codes=expected_codes
        )
        validations['status_code'] = status_result.to_dict()
        
        # Schema validation (only for successful responses)
        if 200 <= response.status_code < 300:
            response_schema = self.parser.get_response_schema(
                endpoint_info['path'], 
                endpoint_info['method'], 
                str(response.status_code)
            )
            
            if response_schema:
                schema_result = self.validators['schema'].validate(response, response_schema)
                validations['schema'] = schema_result.to_dict()
        
        # Header validation
        header_result = self.validators['header'].validate(response, {})
        validations['headers'] = header_result.to_dict()
        
        return validations
    

    def _get_request_details(self, request: requests.PreparedRequest) -> Dict[str, Any]:
        """Extract request details for reporting"""
        details = {
            'method': request.method,
            'url': request.url,
            'headers': dict(request.headers) if request.headers else {}
        }
        
        if request.body:
            # Try to parse JSON body
            try:
                if isinstance(request.body, bytes):
                    body_str = request.body.decode('utf-8')
                else:
                    body_str = request.body
                details['body'] = body_str
            except:
                details['body'] = '<Binary data>'
        
        return details
    
    def _get_response_details(self, response: requests.Response) -> Dict[str, Any]:
        """Extract response details for reporting"""
        details = {
            'status_code': response.status_code,
            'reason': response.reason,
            'headers': dict(response.headers),
            'size': len(response.content)
        }
        
        # Include response body if configured and reasonable size
        max_size = settings.get('reporting.max_response_body_size', 1024)
        if settings.get('reporting.include_response_body', True) and len(response.content) <= max_size:
            try:
                details['body'] = response.text
            except:
                details['body'] = '<Unable to decode response body>'
        
        return details
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of validation results"""
        if not self.results:
            return {'total': 0, 'passed': 0, 'failed': 0, 'success_rate': 0}
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r['success'])
        failed = total - passed
        
        return {
            'total': total,
            'passed': passed,
            'failed': failed,
            'success_rate': (passed / total * 100) if total > 0 else 0,
            'average_response_time': sum(r.get('response_time', 0) for r in self.results) / total
        }
