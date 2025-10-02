from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import requests

class ValidationResult:
    """Container for validation results"""
    
    def __init__(self, valid: bool, message: str = "", details: Optional[Dict] = None):
        self.valid = valid
        self.message = message
        self.details = details or {}
        self.errors = []
        self.warnings = []
    
    def add_error(self, error: str, details: Optional[Dict] = None):
        """Add an error to the result"""
        self.errors.append({
            'message': error,
            'details': details or {}
        })
        self.valid = False
    
    def add_warning(self, warning: str, details: Optional[Dict] = None):
        """Add a warning to the result"""
        self.warnings.append({
            'message': warning,
            'details': details or {}
        })
    
    def has_errors(self) -> bool:
        """Check if result has errors"""
        return len(self.errors) > 0 or not self.valid
    
    def has_warnings(self) -> bool:
        """Check if result has warnings"""
        return len(self.warnings) > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            'valid': self.valid,
            'message': self.message,
            'details': self.details,
            'errors': self.errors,
            'warnings': self.warnings
        }

class BaseValidator(ABC):
    """Base class for all validators"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def validate(self, response: requests.Response, expected_schema: Dict[str, Any], **kwargs) -> ValidationResult:
        """
        Validate response against expected criteria
        
        Args:
            response: HTTP response object
            expected_schema: Expected schema/specification
            **kwargs: Additional validation parameters
        
        Returns:
            ValidationResult: Result of validation
        """
        pass
    
    def _create_error_result(self, message: str, details: Optional[Dict] = None) -> ValidationResult:
        """Helper to create error result"""
        result = ValidationResult(False, message, details)
        return result
    
    def _create_success_result(self, message: str = "Validation passed") -> ValidationResult:
        """Helper to create success result"""
        return ValidationResult(True, message)