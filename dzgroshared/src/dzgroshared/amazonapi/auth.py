from typing import Optional, Dict, Any
import time
import httpx
import backoff

from dzgroshared.amazonapi.model import AmazonApiObject
import time
from typing import Optional
import httpx
import backoff


class CommonLWAClient:
    """
    Login with Amazon (LWA) authentication client for both SP-API and Advertising API.
    Handles token caching, refresh, and retries on transient errors.
    """

    TOKEN_URL = "https://api.amazon.com/auth/o2/token"

    def __init__(self, config: "AmazonApiObject"):
        self.config = config
        self._expires_at: float = 0.0
        self._access_token: Optional[str] = None

    @property
    async def access_token(self) -> str:
        if not self._access_token or time.time() >= self._expires_at:
            await self._refresh_token()
        assert self._access_token is not None  # helps type checker
        return self._access_token

    @backoff.on_exception(
        backoff.expo,
        (httpx.RequestError, httpx.HTTPStatusError),
        max_tries=3,
        jitter=None,  # deterministic backoff (can enable full_jitter=True if needed)
    )
    async def _refresh_token(self) -> None:
        """Refresh the LWA access token."""
        if self.config.refreshtoken:
            payload = {
                "grant_type": "refresh_token",
                "refresh_token": self.config.refreshtoken,
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret,
            }
        elif self.config.scope:
            payload = {
                "grant_type": "client_credentials",
                "scope": self.config.scope,
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret,
            }
        else:
            raise ValueError("Either refresh_token or scope must be provided")

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(self.TOKEN_URL, data=payload)
            resp.raise_for_status()

        token_data = resp.json()
        self._access_token = token_data["access_token"]
        # refresh 30s before actual expiry to be safe
        self._expires_at = time.time() + token_data.get("expires_in", 3600) - 30

class Onboard:

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    async def generateRefreshToken(self, code: str)->str:
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