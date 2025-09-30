import yaml
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

class OpenAPIParser:
    """Parser for OpenAPI 3.0+ specifications"""
    
    def __init__(self, spec_path: Union[str, Path]):
        self.spec_path = Path(spec_path)
        self.spec = self.load_spec()
        self.base_url = self.get_base_url()
        self.paths = self.spec.get('paths', {})
        self.components = self.spec.get('components', {})
    
    def load_spec(self) -> Dict[str, Any]:
        # Load OpenAPI specification from file
        if not self.spec_path.exists():
            raise FileNotFoundError(f"Spec file not found: {self.spec_path}")

        try:
            with open(self.spec_path, 'r', encoding='utf-8') as file:
                if self.spec_path.suffix.lower() in ['.yaml', '.yml']:
                    return yaml.safe_load(file)
                else:
                    return json.load(file)
        except (yaml.YAMLError, json.JSONDecodeError) as e:
            raise ValueError(f"Invalid spec file format: {e}")
    
    def get_endpoint(self, path: str, method: str) -> Optional[Dict[str, Any]]:
        # Get specific endpoint information
        path_item = self.path.get(path, {})
        operation = path_item.get(method.lower(), {})

        if not operation:
            return None
        
        return {
            'path': path,
            'method': method.upper(),
            'operation_id': operation.get('operationId', f"{method}_{path}"),
            'summary': operation.get('summary', ''),
            'description': operation.get('description', ''),
            'parameters': operation.get('parameters', []),
            'request_body': operation.get('requestBody', {}),
            'responses': operation.get('responses', {}),
            'tags': operation.get('tags', []),
            'security': operation.get('security',[])
        }
       

    def get_all_endpoints(self) -> List[Dict[str, Any]]:
        """Get all API endpoints from the specification"""
        endpoints = []
        
        for path, path_item in self.paths.items():
            for method, operation in path_item.items():
                if method.lower() in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']:
                    endpoint_info = {
                        'path': path,
                        'method': method.upper(),
                        'operation_id': operation.get('operationId', f"{method}_{path}"),
                        'summary': operation.get('summary', ''),
                        'description': operation.get('description', ''),
                        'parameters': operation.get('parameters', []),
                        'request_body': operation.get('requestBody', {}),
                        'responses': operation.get('responses', {}),
                        'tags': operation.get('tags', []),
                        'security': operation.get('security', [])
                    }
                    endpoints.append(endpoint_info)
        
        return endpoints
    
    def get_base_url(self) -> str:
        """Extract base URL from specification"""
        servers = self.spec.get('servers', [])
        if servers:
            return servers[0].get('url', '')
        return ''
    

    def get_parameters(self, path: str, method: str) -> List[Dict[str, Any]]:
        """Get parameters for specific endpoint"""
        endpoint = self.get_endpoint(path, method)
        if not endpoint:
            return []
        
        parameters = []
        for param in endpoint.get('parameters', []):
            # Resolve $ref if present
            if '$ref' in param:
                param = self.resolve_reference(param['$ref'])
            
            parameters.append(param)
        
        return parameters
