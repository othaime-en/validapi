import unittest
import tempfile
import yaml
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src"))

from parsers.openapi_parser import OpenAPIParser

class TestOpenAPIParser(unittest.TestCase):
    
    def setUp(self):
        """Create a temporary OpenAPI spec for testing"""
        self.test_spec = {
            "openapi": "3.0.3",
            "info": {
                "title": "Test API",
                "version": "1.0.0"
            },
            "servers": [
                {"url": "https://api.example.com"}
            ],
            "paths": {
                "/users": {
                    "get": {
                        "operationId": "getUsers",
                        "summary": "Get all users",
                        "responses": {
                            "200": {
                                "description": "Success",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "array",
                                            "items": {"$ref": "#/components/schemas/User"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "name": {"type": "string"}
                        }
                    }
                }
            }
        }
        
        # Create temporary file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        yaml.dump(self.test_spec, self.temp_file)
        self.temp_file.close()
        
        self.parser = OpenAPIParser(self.temp_file.name)
    
    def tearDown(self):
        """Clean up temporary file"""
        Path(self.temp_file.name).unlink()
    
    def test_load_spec(self):
        """Test loading OpenAPI specification"""
        self.assertEqual(self.parser.spec['openapi'], '3.0.3')
        self.assertEqual(self.parser.spec['info']['title'], 'Test API')
    
    def test_get_base_url(self):
        """Test extracting base URL"""
        self.assertEqual(self.parser.base_url, 'https://api.example.com')
    
    def test_get_all_endpoints(self):
        """Test getting all endpoints"""
        endpoints = self.parser.get_all_endpoints()
        self.assertEqual(len(endpoints), 1)
        
        endpoint = endpoints[0]
        self.assertEqual(endpoint['path'], '/users')
        self.assertEqual(endpoint['method'], 'GET')
        self.assertEqual(endpoint['operation_id'], 'getUsers')
    
    def test_get_endpoint(self):
        """Test getting specific endpoint"""
        endpoint = self.parser.get_endpoint('/users', 'GET')
        self.assertIsNotNone(endpoint)
        self.assertEqual(endpoint['summary'], 'Get all users')
    
    def test_resolve_reference(self):
        """Test resolving $ref references"""
        user_schema = self.parser.resolve_reference('#/components/schemas/User')
        self.assertEqual(user_schema['type'], 'object')
        self.assertIn('id', user_schema['properties'])
    
    def test_get_response_schema(self):
        """Test getting response schema"""
        schema = self.parser.get_response_schema('/users', 'GET', '200')
        self.assertIsNotNone(schema)
        self.assertEqual(schema['type'], 'array')

if __name__ == '__main__':
    unittest.main()