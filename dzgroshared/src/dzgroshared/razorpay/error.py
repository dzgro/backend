from typing import Callable, TypeVar, Awaitable
import functools
import httpx
from dzgroshared.db.model import DzgroError, ErrorDetail, ErrorList

T = TypeVar("T")

def razorpay_error_wrapper(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> T:
        try:
            return await func(*args, **kwargs)
        except httpx.HTTPStatusError as exc:
            detail: ErrorDetail
            try: detail = ErrorDetail(**exc.response.json())
            except Exception: detail = ErrorDetail(code=400, description=str(exc))
        except Exception as exc: detail = ErrorDetail(code=400, description=str(exc))
        error_list = ErrorList(errors=[detail])
        raise DzgroError(errors=error_list, status_code=detail.code)
    return wrapper