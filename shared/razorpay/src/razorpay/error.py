from typing import Callable, TypeVar, Awaitable
import functools
import httpx
from models.model import ErrorDetail

T = TypeVar("T")

class RazorpayError(Exception):
    def __init__(self, error_detail: ErrorDetail):
        self.error_detail = error_detail
        super().__init__(str(error_detail))

def razorpay_error_wrapper(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> T:
        try:
            return await func(*args, **kwargs)
        except httpx.HTTPStatusError as exc:
            try:
                raise RazorpayError(ErrorDetail(**exc.response.json()))
            except Exception:
                raise RazorpayError(ErrorDetail(code="HTTP_ERROR", description=str(exc)))
        except Exception as exc:
            raise RazorpayError(
                ErrorDetail(
                    code="UNKNOWN_ERROR",
                    description=str(exc)
                )
            )
    return wrapper