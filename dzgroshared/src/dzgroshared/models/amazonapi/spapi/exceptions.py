from typing import Optional, Dict, Any

class SPAPIError(Exception):
    """Base exception for all SPAPI errors."""
    pass

class SPAPIAuthError(SPAPIError):
    """Authentication related errors."""
    pass

class SPAPIRequestError(SPAPIError):
    """API request related errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data or {} 