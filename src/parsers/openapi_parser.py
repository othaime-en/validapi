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
        with open(self.spec_path, 'r', encoding='utf-8') as file:
            if self.spec_path.suffix.lower() in ['.yaml', '.yml']:
                return yaml.safe_load(file)
            else:
                return json.load(file)
    
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
            'request_body': operation.get('request_body', {}),
            'responses': operation.get('responses', {}),
            'tags': operation.get('tags', []),
            'security': operation.get('security',[])
        }
       

    def get_parameters(self, path: str, method: str) -> List[Dict[str, Any]]:
        # Get parameters for specific endpoint
        parameters = []
        return parameters
