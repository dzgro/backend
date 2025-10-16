from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from dzgroshared.db.model import DzgroError, ErrorDetail

def register_exception_handlers(app):
    @app.exception_handler(DzgroError)
    async def custom_api_exception_handler(request: Request, exc: DzgroError):
        return JSONResponse(
            status_code=400,
            content={"errors": [{'errortype': 'Dzgro', **e.model_dump(exclude_none=True)} for e in exc.errors.errors]}
        )
    
    @app.exception_handler(ValueError)
    async def value_error_exception_handler(request: Request, exc: ValueError):
        return JSONResponse(
            status_code=400,
            content={"errors": [{'errortype': 'ValueError', 'message': exc.args[0] if exc.args else str(exc)}]}
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
            status_code=400,
            content={"errors": [{'errortype': 'Pydantic', **error.model_dump(exclude_none=True)}]}
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
            status_code=400,
            content={"errors": [{'errortype': 'Unhandled', **error.model_dump(exclude_none=True)}]}
        )
