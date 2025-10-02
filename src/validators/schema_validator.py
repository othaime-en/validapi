import json
from typing import Dict, Any, List
import requests
import jsonschema
from jsonschema import Draft7Validator
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
    

