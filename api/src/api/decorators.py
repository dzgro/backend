import hashlib
from fastapi import Response, Request
from functools import wraps
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from functools import wraps
from fastapi.responses import JSONResponse

def enforce_response_model(model_cls):
    """
    Decorator to force Pydantic validation on endpoint responses.
    Ensures model_validator/field_validator run even if returning dicts.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            import asyncio
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            validated = model_cls.model_validate(result)
            return JSONResponse(validated.model_dump(mode="json"))
        return wrapper
    return decorator


def cache_control(max_age: int = 7200):  # default 2h
    """
    Decorator to add Cache-Control + Expires + Age + ETag headers.
    - max_age: cache duration in seconds
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            from typing import Optional
            request: Optional[Request] = kwargs.get("request")

            # Call the route handler
            result = await func(*args, **kwargs)

            # Ensure result is a Response
            if isinstance(result, Response):
                response = result
                body = response.body
            else:
                response = JSONResponse(content=result.model_dump(mode="json") if isinstance(result, BaseModel) else result)
                body = response.body

            # Generate ETag from body
            etag = hashlib.md5(body).hexdigest()

            # Handle conditional request
            if request and request.headers.get("if-none-match") == etag:
                # Return 304 Not Modified
                return Response(status_code=304, headers={
                    "ETag": etag,
                    "Cache-Control": f"public, max-age={max_age}",
                    "Expires": (datetime.now() + timedelta(seconds=max_age)).strftime(
                        "%a, %d %b %Y %H:%M:%S GMT"
                    ),
                    "Age": "0"
                })

            # Add caching headers
            response.headers["Cache-Control"] = f"public, max-age={max_age}"
            response.headers["ETag"] = etag
            response.headers["Age"] = "0"
            response.headers["Expires"] = (
                datetime.now() + timedelta(seconds=max_age)
            ).strftime("%a, %d %b %Y %H:%M:%S GMT")

            return response

        return wrapper
    return decorator
