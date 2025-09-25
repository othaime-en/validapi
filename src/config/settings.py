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
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as file:
                config = yaml.safe_load(file) or {}
                return config
        except FileNotFoundError:
            print(f"Config file not found at {self.config_path}, using defaults")
            return self.get_default_config()
        except yaml.YAMLError as e:
            print(f"Error parsing config file: {e}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            'validation': {
                'strict_mode': True,
                'timeout': 30,
                'max_retries': 3,
                'validate_examples': True
            },
            'reporting': {
                'output_format': 'html',
                'output_dir': 'reports',
                'include_request_details': True,
                'include_response_body': True
            },
            'http': {
                'headers': {
                    'User-Agent': 'API-Validator/1.0'
                },
                'follow_redirects': True,
                'verify_ssl': True
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def update(self, key: str, value: Any) -> None:
        """Update configuration value using dot notation"""
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