import time
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
        """
        Validate a single endpoint
        
        Args:
            path: API endpoint path
            method: HTTP method
            test_data: Optional test data for request
        
        Returns:
            Dict containing validation results
        """        
        start_time = time.time()
        
        # Get endpoint information from spec
        endpoint_info = self.parser.get_endpoint(path, method)
        if not endpoint_info:
            return {
                'path': path,
                'method': method,
                'success': False,
                'error': f'Endpoint not found in specification: {method} {path}',
                'duration': 0
            }
        
        try:
            # Make HTTP request
            response = self._make_request(path, method, test_data)
            
            # Validate response
            validation_results = self._validate_response(response, endpoint_info)
            
            duration = time.time() - start_time
            
            result = {
                'path': path,
                'method': method,
                'success': all(v['valid'] for v in validation_results.values()),
                'status_code': response.status_code,
                'response_time': duration,
                'validations': validation_results,
                'request_details': self._get_request_details(response.request),
                'response_details': self._get_response_details(response),
                'endpoint_info': {
                    'operation_id': endpoint_info.get('operation_id'),
                    'summary': endpoint_info.get('summary'),
                    'tags': endpoint_info.get('tags', [])
                }
            }
            
            return result
            
        except requests.RequestException as e:
            duration = time.time() - start_time
            return {
                'path': path,
                'method': method,
                'success': False,
                'error': f'Request failed: {str(e)}',
                'duration': duration,
                'validations': {},
                'request_details': {},
                'response_details': {}
            }
    
    def validate_all_endpoints(self, test_data: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Validate all endpoints in the specification
        
        Args:
            test_data: Optional test data for requests
        
        Returns:
            List of validation results 
        """
        endpoints = self.parser.get_all_endpoints()
        results = []
        
        total_endpoints = len(endpoints)
        print(f"Validating {total_endpoints} endpoints...")
        
        for i, endpoint in enumerate(endpoints, 1):
            print(f"[{i}/{total_endpoints}] Testing {endpoint['method']} {endpoint['path']}")
            
            # Get test data for this specific endpoint
            endpoint_test_data = test_data.get(endpoint['path'], {}).get(endpoint['method'].lower()) if test_data else None
            
            result = self.validate_endpoint(endpoint['path'], endpoint['method'], endpoint_test_data)
            results.append(result)
            
            # Add delay between requests if configured
            delay = settings.get('execution.delay_between_requests', 0)
            if delay > 0:
                time.sleep(delay)
            
            # Stop on first failure if configured
            if not result['success'] and settings.get('execution.stop_on_first_failure', False):
                print("Stopping on first failure as configured")
                break
        
        self.results = results
        return results
    

    
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
                # Pass the full spec for reference resolution
                schema_result = self.validators['schema'].validate(
                    response, 
                    response_schema,
                    spec=self.parser.spec 
                )
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