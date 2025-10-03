import json
from typing import Dict, Any, List, Optional
import requests
import jsonschema
from jsonschema import Draft7Validator, ValidationError
from .base import BaseValidator, ValidationResult

class SchemaValidator(BaseValidator):
    """Validates JSON responses against JSON Schema"""
    
    def __init__(self):
        super().__init__("Schema Validator")
    
    def validate(self, response: requests.Response, expected_schema: Dict[str, Any], **kwargs) -> ValidationResult:
        """
        Validate response JSON against schema
        
        Args:
            response: HTTP response object
            expected_schema: JSON Schema to validate against
            **kwargs: Additional validation parameters
        
        Returns:
            ValidationResult: Validation result
        """
        result = ValidationResult(True)
        
        try:
            # Check if response has JSON content
            if not self._is_json_response(response):
                result.add_error("Response is not JSON", {
                    'content_type': response.headers.get('content-type', 'unknown'),
                    'status_code': response.status_code
                })
                return result
            
            # Parse response JSON
            try:
                response_data = response.json()
            except json.JSONDecodeError as e:
                result.add_error(f"Invalid JSON in response: {str(e)}", {
                    'response_text': response.text[:500]  # First 500 chars
                })
                return result
            
            # Validate against schema
            if expected_schema:
                schema_errors = self._validate_against_schema(response_data, expected_schema)
                for error in schema_errors:
                    result.add_error(f"Schema validation error: {error['message']}", error['details'])
            
            # Additional validations
            self._validate_response_structure(response_data, result)
            
            if result.valid:
                result.message = "Response validates against schema"
            
        except Exception as e:
            result.add_error(f"Unexpected validation error: {str(e)}")
        
        return result
    
    def _is_json_response(self, response: requests.Response) -> bool:
        """Check if response contains JSON"""
        content_type = response.headers.get('content-type', '').lower()
        return 'application/json' in content_type or content_type.endswith('/json')
    
    def _validate_against_schema(self, data: Any, schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate data against JSON schema"""
        errors = []
        
        try:
            # Create validator
            validator = Draft7Validator(schema)
            
            # Validate and collect errors
            for error in validator.iter_errors(data):
                error_details = {
                    'path': list(error.absolute_path),
                    'invalid_value': error.instance,
                    'schema_path': list(error.schema_path),
                    'validator': error.validator,
                    'validator_value': error.validator_value
                }
                
                errors.append({
                    'message': error.message,
                    'details': error_details
                })
        
        except jsonschema.SchemaError as e:
            errors.append({
                'message': f"Invalid schema: {e.message}",
                'details': {'schema_error': str(e)}
            })
        
        return errors
    
    def _validate_response_structure(self, data: Any, result: ValidationResult):
        """Perform additional structural validations"""
        
        # Check for common API response patterns
        if isinstance(data, dict):
            # Check for error responses
            if 'error' in data and isinstance(data['error'], str):
                result.add_warning("Response contains error field", {
                    'error_message': data['error']
                })
            
            # Check for pagination patterns
            if 'data' in data and isinstance(data['data'], list):
                if 'page' in data or 'limit' in data or 'total' in data:
                    result.details['pagination_detected'] = True
            
            # Check for empty required fields
            self._check_empty_fields(data, result)
    
    def _check_empty_fields(self, data: Dict[str, Any], result: ValidationResult, path: str = ""):
        """Check for empty or null required fields"""
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key
            
            if value is None:
                result.add_warning(f"Null value found at {current_path}")
            elif value == "":
                result.add_warning(f"Empty string found at {current_path}")
            elif isinstance(value, dict) and len(value) == 0:
                result.add_warning(f"Empty object found at {current_path}")
            elif isinstance(value, list) and len(value) == 0:
                result.add_warning(f"Empty array found at {current_path}")
            elif isinstance(value, dict):
                self._check_empty_fields(value, result, current_path)


class StatusCodeValidator(BaseValidator):
    """Validates HTTP status codes"""
    
    def __init__(self):
        super().__init__("Status Code Validator")
    
    def validate(self, response: requests.Response, expected_schema: Dict[str, Any], **kwargs) -> ValidationResult:
        """
        Validate response status code
        
        Args:
            response: HTTP response object
            expected_schema: Not used for status code validation
            expected_codes: List of expected status codes
        
        Returns:
            ValidationResult: Validation result
        """
        expected_codes = kwargs.get('expected_codes', [])
        
        if not expected_codes:
            return ValidationResult(True, "No expected status codes specified")
        
        actual_code = response.status_code
        expected_codes_str = [str(code) for code in expected_codes]
        
        if str(actual_code) in expected_codes_str:
            return ValidationResult(True, f"Status code {actual_code} is expected")
        else:
            return self._create_error_result(
                f"Unexpected status code: {actual_code}",
                {
                    'actual_code': actual_code,
                    'expected_codes': expected_codes,
                    'reason': response.reason
                }
            )

class HeaderValidator(BaseValidator):
    """Validates HTTP response headers"""
    
    def __init__(self):
        super().__init__("Header Validator")
    
    def validate(self, response: requests.Response, expected_schema: Dict[str, Any], **kwargs) -> ValidationResult:
        """
        Validate response headers
        
        Args:
            response: HTTP response object
            expected_schema: Schema containing expected headers
            **kwargs: Additional validation parameters
        
        Returns:
            ValidationResult: Validation result
        """
        result = ValidationResult(True)
        expected_headers = kwargs.get('expected_headers', {})
        
        if not expected_headers:
            return ValidationResult(True, "No expected headers specified")
        
        response_headers = {k.lower(): v for k, v in response.headers.items()}
        
        for header_name, expected_value in expected_headers.items():
            header_name_lower = header_name.lower()
            
            if header_name_lower not in response_headers:
                result.add_error(f"Missing expected header: {header_name}")
                continue
            
            actual_value = response_headers[header_name_lower]
            
            # If expected_value is None, we just check for presence
            if expected_value is not None and actual_value != expected_value:
                result.add_error(
                    f"Header value mismatch for {header_name}",
                    {
                        'expected': expected_value,
                        'actual': actual_value
                    }
                )
        
        # Check for security headers
        self._check_security_headers(response_headers, result)
        
        if result.valid:
            result.message = "Headers validation passed"
        
        return result
    
    def _check_security_headers(self, headers: Dict[str, str], result: ValidationResult):
        """Check for common security headers"""
        security_headers = {
            'x-content-type-options': 'nosniff',
            'x-frame-options': None,  # Any value is good
            'x-xss-protection': None,
            'strict-transport-security': None,
            'content-security-policy': None
        }
        
        for header, expected_value in security_headers.items():
            if header not in headers:
                result.add_warning(f"Missing security header: {header}")
            elif expected_value and headers[header] != expected_value:
                result.add_warning(
                    f"Security header {header} has unexpected value",
                    {
                        'expected': expected_value,
                        'actual': headers[header]
                    }
                )
