from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from models.model import ErrorList, ErrorDetail

class APIError(Exception):
    def __init__(self, error_list: ErrorList, status_code: int = 500):
        self.error_list = error_list
        self.status_code = status_code
        super().__init__(str(error_list))