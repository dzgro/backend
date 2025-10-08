import logging
from typing import Optional, Dict, Any, Type, TypeVar, Generic
import httpx
from pydantic import BaseModel, ValidationError
from dzgroshared.amazonapi.auth import CommonLWAClient
from dzgroshared.db.model import DzgroError
from dzgroshared.amazonapi.model import AmazonApiObject
from dzgroshared.db.model import ErrorList, ErrorDetail

logger = logging.getLogger(__name__)

ResponseT = TypeVar('ResponseT', bound=BaseModel)

class BaseClient(Generic[ResponseT]):
    """Base async client for Amazon APIs (SP-API and Advertising API)."""
    config: AmazonApiObject
    client_id: str

    def __init__(self, config: AmazonApiObject):
        self.config = config
        self.auth_client = CommonLWAClient(self.config)  # expects AmazonApiObject to have required fields

    async def _get_headers(self, operation: str = "") -> Dict[str, str]:
        access_token = await self.auth_client.access_token
        if not access_token:
            error = ErrorList(errors=[ErrorDetail(code=400, message="No access token available", details=None)])
            raise DzgroError(error)
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if self.config.isad:
            headers["Authorization"] = f"Bearer {access_token}"
            headers["Amazon-Advertising-API-ClientId"] = self.config.client_id
            if self.config.profile: headers["Amazon-Advertising-API-Scope"] = str(self.config.profile)
        else: headers["x-amz-access-token"] = access_token
        return headers

    async def _request(
        self,
        method: str,
        path: str,
        operation: str,
        response_model: Type[ResponseT],
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> ResponseT:
        request_headers = await self._get_headers(operation)
        if headers: request_headers.update(headers)
        url = f"{self.config.url}{path}"
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=request_headers
            )
        try:
            response.raise_for_status()
            obj = response.json()
            return response_model.model_validate(obj)
        except httpx.HTTPStatusError as e:
            try:
                obj = response.json()
                error = ErrorList.model_validate(obj)
            except ValidationError:
                error = ErrorList(errors=[ErrorDetail(code=response.status_code, message=str(e), details=str(response.text))])
            raise DzgroError(error)