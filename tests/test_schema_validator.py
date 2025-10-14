import unittest
import json
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from validators.schema_validator import SchemaValidator, StatusCodeValidator, HeaderValidator

class TestSchemaValidator(unittest.TestCase):
    
    def setUp(self):
        self.validator = SchemaValidator()
    
    def test_valid_json_response(self):
        """Test validation of valid JSON response"""
        # Mock response
        response = Mock()
        response.headers = {'content-type': 'application/json'}
        response.json.return_value = {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com"
        }
        
        # Schema
        schema = {
            "type": "object",
            "required": ["id", "name", "email"],
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "email": {"type": "string", "format": "email"}
            }
        }
        
        result = self.validator.validate(response, schema)
        self.assertTrue(result.valid)
        self.assertFalse(result.has_errors())
    
    def test_invalid_json_response(self):
        """Test validation of invalid JSON response"""
        response = Mock()
        response.headers = {'content-type': 'application/json'}
        response.json.return_value = {
            "id": "not_a_number",  # Should be integer
            "name": "John Doe"
            # Missing required email field
        }
        
        schema = {
            "type": "object",
            "required": ["id", "name", "email"],
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "email": {"type": "string"}
            }
        }
        
        result = self.validator.validate(response, schema)
        self.assertFalse(result.valid)
        self.assertTrue(result.has_errors())
        self.assertTrue(len(result.errors) >= 2)  # Type error and missing field
    
    def test_non_json_response(self):
        """Test validation of non-JSON response"""
        response = Mock()
        response.headers = {'content-type': 'text/html'}
        
        result = self.validator.validate(response, {})
        self.assertFalse(result.valid)
        self.assertTrue(result.has_errors())

class TestStatusCodeValidator(unittest.TestCase):
    
    def setUp(self):
        self.validator = StatusCodeValidator()
    
    def test_expected_status_code(self):
        """Test validation with expected status code"""
        response = Mock()
        response.status_code = 200
        response.reason = "OK"
        
        result = self.validator.validate(response, {}, expected_codes=[200, 201])
        self.assertTrue(result.valid)
    
    def test_unexpected_status_code(self):
        """Test validation with unexpected status code"""
        response = Mock()
        response.status_code = 404
        response.reason = "Not Found"
        
        result = self.validator.validate(response, {}, expected_codes=[200, 201])
        self.assertFalse(result.valid)
        self.assertTrue(result.has_errors())

class TestHeaderValidator(unittest.TestCase):
    
    def setUp(self):
        self.validator = HeaderValidator()
    
    def test_expected_headers_present(self):
        """Test validation when expected headers are present"""
        response = Mock()
        response.headers = {
            'Content-Type': 'application/json',
            'X-API-Version': '1.0'
        }
        
        expected_headers = {
            'Content-Type': 'application/json',
            'X-API-Version': '1.0'
        }
        
        result = self.validator.validate(response, {}, expected_headers=expected_headers)
        self.assertTrue(result.valid)
    
    def test_missing_expected_headers(self):
        """Test validation when expected headers are missing"""
        response = Mock()
        response.headers = {
            'Content-Type': 'application/json'
        }
        
        expected_headers = {
            'Content-Type': 'application/json',
            'X-API-Version': '1.0'
        }
        
        result = self.validator.validate(response, {}, expected_headers=expected_headers)
        self.assertFalse(result.valid)
        self.assertTrue(result.has_errors())

if __name__ == '__main__':
    unittest.main()