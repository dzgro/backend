"""
Local Development Authentication Middleware

This middleware automatically injects authentication headers for FastAPI UI requests
when running in LOCAL environment. It detects requests from Swagger UI/ReDoc and
provides the necessary Authorization and marketplace headers transparently.

Only active when:
- Environment is ENVIRONMENT.LOCAL
- Request is detected as coming from FastAPI UI (Swagger/ReDoc)

Constants are self-contained - no dependency on test project.
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from dzgroshared.db.enums import ENVIRONMENT
from dzgroshared.secrets.client import SecretManager
from boto3.session import Session
import functools
import time
from typing import Optional

# Local development constants - no dependency on test project
LOCAL_DEV_EMAIL = "dzgrotechnologies@gmail.com"
LOCAL_DEV_MARKETPLACE_ID = "6895638c452dc4315750e826"


class LocalDevAuthMiddleware(BaseHTTPMiddleware):
    """Middleware to auto-inject auth headers for FastAPI UI in local development"""
    
    def __init__(self, app, environment: Optional[ENVIRONMENT] = None):
        super().__init__(app)
        self.environment = environment
        self._cached_token: Optional[str] = None
        self._token_expires_at: float = 0
        self._token_cache_duration = 3600  # 1 hour
    
    def _is_fastapi_ui_request(self, request: Request) -> bool:
        """
        Detect if request is from FastAPI UI (Swagger/ReDoc)
        
        Uses multiple detection methods:
        1. Direct docs page access
        2. Referer header from docs pages  
        3. User-agent patterns from Swagger UI
        4. JSON requests without existing auth (likely from docs)
        """
        # Direct docs page access
        if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
            return True
            
        # Request from docs page (referer check)
        referer = request.headers.get("referer", "")
        if "/docs" in referer or "/redoc" in referer:
            return True
            
        # Swagger UI user agent patterns
        user_agent = request.headers.get("user-agent", "").lower()
        if any(ua in user_agent for ua in ["swagger-ui", "openapi", "redoc"]):
            return True
            
        # JSON request without custom auth headers (likely from docs)
        # This catches API requests made through the FastAPI UI
        accept_header = request.headers.get("accept", "")
        has_json_accept = "application/json" in accept_header
        has_no_auth = not request.headers.get("authorization")
        has_no_custom_auth = not request.headers.get("x-api-key")
        is_not_browser = "text/html" not in accept_header
        
        if (has_json_accept and has_no_auth and has_no_custom_auth and 
            is_not_browser and request.method in ["GET", "POST", "PUT", "DELETE", "PATCH"]):
            return True
            
        return False
    
    def _get_local_dev_constants(self):
        """Get local development constants"""
        return {
            "email": LOCAL_DEV_EMAIL,
            "marketplace_id": LOCAL_DEV_MARKETPLACE_ID
        }
    
    def _generate_auth_token(self) -> str:
        """
        Generate authentication token using the same method as test fixtures
        Includes caching to avoid repeated Cognito calls
        """
        current_time = time.time()
        
        # Return cached token if still valid
        if self._cached_token and current_time < self._token_expires_at:
            return self._cached_token
        
        try:
            # Get secrets (same as main app)
            if self.environment is None:
                raise ValueError("Environment not set")
            secrets = SecretManager(self.environment).secrets
            constants = self._get_local_dev_constants()
            
            # Create Cognito client
            client = Session().client(
                service_name='cognito-idp',
                region_name='ap-south-1'
            )
            
            # Authenticate using AWS Cognito
            response = client.initiate_auth(
                ClientId=secrets.COGNITO_APP_CLIENT_ID,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': constants["email"],
                    'PASSWORD': secrets.USER_DUMMY_PASSWORD
                }
            )
            
            access_token = response['AuthenticationResult'].get('AccessToken')
            if not access_token:
                raise ValueError("Access Token Not Generated")
            
            # Cache the token
            self._cached_token = access_token
            self._token_expires_at = current_time + self._token_cache_duration
            
            print(f"🔑 Generated new auth token for FastAPI UI (cached for {self._token_cache_duration}s)")
            return access_token
            
        except Exception as e:
            print(f"❌ Error generating auth token for FastAPI UI: {e}")
            raise
    
    def _inject_auth_headers(self, request: Request) -> None:
        """Inject Authorization and marketplace headers into the request"""
        try:
            constants = self._get_local_dev_constants()
            
            # Inject Authorization header if missing
            if not request.headers.get("authorization"):
                token = self._generate_auth_token()
                request.headers.__dict__["_list"].append(
                    (b"authorization", f"Bearer {token}".encode())
                )
                print(f"🔒 Injected Authorization header for FastAPI UI request: {request.method} {request.url.path}")
            
            # Inject marketplace header if missing  
            if not request.headers.get("marketplace"):
                request.headers.__dict__["_list"].append(
                    (b"marketplace", constants["marketplace_id"].encode())
                )
                print(f"🏪 Injected marketplace header for FastAPI UI request: {request.method} {request.url.path}")
                
        except Exception as e:
            print(f"❌ Error injecting auth headers: {e}")
            # Don't fail the request, just log the error
    
    async def dispatch(self, request: Request, call_next):
        """Main middleware dispatch method"""
        
        # Only process requests in LOCAL environment
        if self.environment == ENVIRONMENT.LOCAL:
            
            # Check if this is a FastAPI UI request
            if self._is_fastapi_ui_request(request):
                print(f"🎯 Detected FastAPI UI request: {request.method} {request.url.path}")
                
                # Inject authentication headers
                self._inject_auth_headers(request)
        
        # Continue processing the request
        response = await call_next(request)
        return response


def create_local_dev_auth_middleware_with_secrets(environment: ENVIRONMENT, secrets):
    """
    Factory function to create the local dev auth middleware using pre-loaded secrets
    This approach reuses secrets from the lifespan context, avoiding duplicate secret loading
    """
    
    # Create a single instance for caching
    _cached_token: Optional[str] = None
    _token_expires_at: float = 0
    _token_cache_duration = 3600  # 1 hour
    
    def _get_local_dev_constants():
        """Get local development constants"""
        return {
            "email": LOCAL_DEV_EMAIL,
            "marketplace_id": LOCAL_DEV_MARKETPLACE_ID
        }
    
    def _generate_auth_token() -> str:
        """Generate authentication token with caching using pre-loaded secrets"""
        nonlocal _cached_token, _token_expires_at
        
        current_time = time.time()
        
        # Return cached token if still valid
        if _cached_token and current_time < _token_expires_at:
            return _cached_token
        
        try:
            # Use pre-loaded secrets (no duplicate secret loading!)
            constants = _get_local_dev_constants()
            
            # Create Cognito client
            client = Session().client(
                service_name='cognito-idp',
                region_name='ap-south-1'
            )
            
            # Authenticate using AWS Cognito  
            response = client.initiate_auth(
                ClientId=secrets.COGNITO_APP_CLIENT_ID,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': constants["email"],
                    'PASSWORD': secrets.USER_DUMMY_PASSWORD
                }
            )
            
            access_token = response['AuthenticationResult'].get('AccessToken')
            if not access_token:
                raise ValueError("Access Token Not Generated")
            
            # Cache the token
            _cached_token = access_token
            _token_expires_at = current_time + _token_cache_duration
            
            print(f"🔑 Generated new auth token for FastAPI UI using shared secrets (cached for {_token_cache_duration}s)")
            return access_token
            
        except Exception as e:
            print(f"❌ Error generating auth token for FastAPI UI: {e}")
            raise



    
    def _is_fastapi_ui_request(request: Request) -> bool:
        """Detect if request is from FastAPI UI (Swagger/ReDoc)"""
        # Direct docs page access
        if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
            return True
            
        # Request from docs page (referer check)
        referer = request.headers.get("referer", "")
        if "/docs" in referer or "/redoc" in referer:
            return True
            
        # Swagger UI user agent patterns
        user_agent = request.headers.get("user-agent", "").lower()
        if any(ua in user_agent for ua in ["swagger-ui", "openapi", "redoc"]):
            return True
            
        # JSON request without custom auth headers (likely from docs)
        accept_header = request.headers.get("accept", "")
        has_json_accept = "application/json" in accept_header
        has_no_auth = not request.headers.get("authorization")
        has_no_custom_auth = not request.headers.get("x-api-key")
        is_not_browser = "text/html" not in accept_header
        
        if (has_json_accept and has_no_auth and has_no_custom_auth and 
            is_not_browser and request.method in ["GET", "POST", "PUT", "DELETE", "PATCH"]):
            return True
            
        return False
    
    def _inject_auth_headers(request: Request) -> None:
        """Inject Authorization and marketplace headers into the request"""
        try:
            constants = _get_local_dev_constants()
            
            # Inject Authorization header if missing
            if not request.headers.get("authorization"):
                token = _generate_auth_token()
                request.headers.__dict__["_list"].append(
                    (b"authorization", f"Bearer {token}".encode())
                )
                print(f"🔒 Injected Authorization header for FastAPI UI request: {request.method} {request.url.path}")
            
            # Inject marketplace header if missing  
            if not request.headers.get("marketplace"):
                request.headers.__dict__["_list"].append(
                    (b"marketplace", constants["marketplace_id"].encode())
                )
                print(f"🏪 Injected marketplace header for FastAPI UI request: {request.method} {request.url.path}")
                
        except Exception as e:
            print(f"❌ Error injecting auth headers: {e}")
            # Don't fail the request, just log the error
    
    async def middleware(request: Request, call_next):
        """Main middleware function using pre-loaded secrets"""

        # Check if this is a FastAPI UI request
        if _is_fastapi_ui_request(request):
            print(f"🎯 Detected FastAPI UI request: {request.method} {request.url.path}")

            # Inject authentication headers
            _inject_auth_headers(request)

        # Continue processing the request
        response = await call_next(request)
        return response
    
    return middleware


# Legacy function for backward compatibility - creates the same middleware structure
def create_local_dev_auth_middleware(environment: ENVIRONMENT):
    """
    Legacy factory function - kept for backward compatibility
    This version loads secrets independently (less efficient)
    """
    from dzgroshared.secrets.client import SecretManager
    
    print("⚠️  Using legacy middleware - consider using create_local_dev_auth_middleware_with_secrets() for better performance")
    
    # Load secrets independently (not optimal)
    secrets = SecretManager(environment).secrets
    
    # Delegate to the optimized version
    return create_local_dev_auth_middleware_with_secrets(environment, secrets)