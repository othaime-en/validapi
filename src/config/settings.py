import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional

class Settings:
    """Configuration management for API Validator"""
    
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
        self.config_path = Path(config_path)
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        
        try:
            with open(self.config_path, 'r') as file:
                config = yaml.safe_load(file) or {}
                return config
        except FileNotFoundError:
            print(f"Config file not found at {self.config_path}, using defaults")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        
        return {
            'validation': {
                'strict_mode': True,
                'timeout': 15,
                'validate_examples': True
            },
            'reporting': {
                'output_format': 'html',
                'include_request_details': True,
                'include_response_body': True
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def update(self, key: str, value: Any) -> None:
        
        keys = key.split('.')
        config_ref = self.config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config_ref:
                config_ref[k] = {}
            config_ref = config_ref[k]
        
        # Set the value
        config_ref[keys[-1]] = value

# This is the global settings instance
settings = Settings()