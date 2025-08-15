from typing import Optional, Dict, Any
import time
import httpx
import backoff

from dzgroshared.models.amazonapi.model import AmazonApiObject

class CommonLWAClient:
    """Login with Amazon (LWA) authentication client for both SP-API and Advertising API."""
    def __init__(self, config: AmazonApiObject):
        self.config = config
        self.expires_at: Optional[float] = None
        self.accessToken: Optional[str] = None
    @property
    async def access_token(self) -> Optional[str]:
        if not self.accessToken or not self.expires_at or time.time() >= self.expires_at:
            await self._refresh_token()
        return self.accessToken

    @backoff.on_exception(
        backoff.expo,
        httpx.RequestError,
        max_tries=3
    )
    async def _refresh_token(self) -> None:
        data = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
        }
        if self.config.refreshtoken:
            data.update({
                "grant_type": "refresh_token",
                "refresh_token": self.config.refreshtoken
            })
        elif self.config.scope:
            data.update({
                "grant_type": "client_credentials",
                "scope": self.config.scope
            })
        else:
            raise Exception("Either refresh_token or scope must be provided")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.amazon.com/auth/o2/token",
                    data=data
                )
            response.raise_for_status()
            token_data = response.json()
            self.expires_at = time.time() + token_data.get("expires_in", 3600) - 30
            self.accessToken = token_data.get("access_token",None)
        except httpx.HTTPStatusError as e:
            error_msg = f"Token refresh failed: {e.response.status_code} - {e.response.text}"
            raise Exception(error_msg) from e
        except httpx.RequestError as e:
            error_msg = f"Token refresh failed: {str(e)}"
            raise Exception(error_msg) from e 
        
class Onboard:

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    async def generateRefreshToken(self, code: str):
        data = {
            'grant_type' : 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.redirect_uri
        }
        async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.amazon.com/auth/o2/token",
                    data=data,
                    headers={'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'}
                )
        if response.status_code!=200: raise ValueError("Token Could not be generated")
        return response.json()['refresh_token']