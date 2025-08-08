from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import Optional, Dict, Any
from models.model import ErrorDetail

class CustomAPIException(Exception):
    def __init__(self, code: int, description: str, message: Optional[str] = None, details: Optional[str] = None, source: Optional[str] = None, step: Optional[str] = None, reason: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None, status_code: int = 400):
        self.error = ErrorDetail(
            code=code,
            description=description,
            message=message,
            details=details,
            source=source,
            step=step,
            reason=reason,
            metadata=metadata
        )
        self.status_code = status_code

def register_exception_handlers(app):
    @app.exception_handler(CustomAPIException)
    async def custom_api_exception_handler(request: Request, exc: CustomAPIException):
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.error.model_dump()
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        error = ErrorDetail(
            code=400,
            description="Request validation failed",
            message=str(exc),
            details=str(exc.errors()),
            source="request",
            step=None,
            reason=None,
            metadata=None
        )
        return JSONResponse(
            status_code=422,
            content=error.model_dump()
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        error = ErrorDetail(
            code=400,
            description="An unexpected error occurred",
            message=str(exc),
            details=None,
            source="server",
            step=None,
            reason=None,
            metadata=None
        )
        return JSONResponse(
            status_code=500,
            content=error.model_dump()
        )
