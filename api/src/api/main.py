from dzgroshared.client import DzgroSharedClient
from dzgroshared.secrets.model import DzgroSecrets
from fastapi import Depends, FastAPI, Request, Security
from fastapi.responses import Response, RedirectResponse, JSONResponse
from api.exception_handlers import register_exception_handlers
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.security import APIKeyHeader
import io, yaml, os, functools, time, asyncio, json
from fastapi.openapi.utils import get_openapi
from dzgroshared.db.pricing.model import Pricing
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import _StreamingResponse

from dotenv import load_dotenv
load_dotenv()
from dzgroshared.db.enums import ENVIRONMENT, CountryCode
env = ENVIRONMENT(os.getenv("ENV", None))
if not env: raise ValueError("ENV environment variable not set")


# Move imports to module level for better performance
from dzgroshared.secrets.client import SecretManager
from motor.motor_asyncio import AsyncIOMotorClient

import jwt
def is_running_on_lambda():
    """
    Detect if the application is running on AWS Lambda
    """
    return bool(os.getenv('AWS_LAMBDA_FUNCTION_NAME')) or bool(os.getenv('LAMBDA_RUNTIME_DIR'))


# Import local development middleware (only in LOCAL environment)
if not is_running_on_lambda():
    from api.middleware.local_dev_auth import create_local_dev_auth_middleware_with_secrets


def get_secrets_from_env_or_ssm(environment: ENVIRONMENT):
    """
    Load secrets based on runtime environment:
    - Lambda: Use environment variables only (fail if missing)
    - EC2: Use SSM Parameter Store only
    """
    from dzgroshared.secrets.model import DzgroSecrets
    
    is_lambda = is_running_on_lambda()
    
    if is_lambda:
        print("🔍 Detected Lambda environment - using environment variables")
        # For Lambda: Only use environment variables, validate against DzgroSecrets model
        env_secrets = {}
        missing_secrets = []
        
        # Get all required secrets from DzgroSecrets model fields
        required_secrets = list(DzgroSecrets.model_fields.keys())
        
        for secret_name in required_secrets:
            value = os.getenv(secret_name)
            if value:
                env_secrets[secret_name] = value
            else:
                missing_secrets.append(secret_name)
        
        if missing_secrets:
            raise ValueError(f"Lambda deployment missing required environment variables: {missing_secrets}")
        
        # Create a simple object to mimic SecretManager.secrets
        class EnvSecrets:
            def __init__(self, secrets_dict):
                for key, value in secrets_dict.items():
                    setattr(self, key, value)
        
        print("✅ Successfully loaded all secrets from environment variables")
        return EnvSecrets(env_secrets)
    
    else:
        print("🔍 Detected EC2/local environment - using SSM Parameter Store")
        # For EC2: Only use SSM Parameter Store
        return SecretManager(environment).secrets


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.env = env
        app.state.is_lambda = is_running_on_lambda()  # Store runtime detection
        
        print(f"🚀 Starting application in {'Lambda' if app.state.is_lambda else 'EC2/Local'} environment")
        
        # Load secrets using environment-specific approach
        secrets = await asyncio.to_thread(get_secrets_from_env_or_ssm, env)
        app.state.secrets = secrets
        
        # Setup clients concurrently with error handling - pass secrets as parameters
        async def setup_mongo(secrets):
            return AsyncIOMotorClient(
                secrets.MONGO_DB_CONNECT_URI, 
                appname="dzgro-api",
                maxPoolSize=1,  # Lambda processes one request at a time
                minPoolSize=0,  # No need to maintain connections when idle
                maxIdleTimeMS=900000,  # Keep connection for 15 minutes (Lambda warm period)
                serverSelectionTimeoutMS=10000,  # Faster timeout for Lambda
                connectTimeoutMS=10000,  # Faster connection timeout
                socketTimeoutMS=60000,  # Socket timeout for operations
                heartbeatFrequencyMS=60000  # Heartbeat every minute
            )
        
        async def setup_jwt(secrets):
            jwks_url = f"https://cognito-idp.ap-south-1.amazonaws.com/{secrets.COGNITO_USER_POOL_ID}/.well-known/jwks.json"
            return jwt.PyJWKClient(
                jwks_url,
                cache_keys=True,  # Cache the keys
                max_cached_keys=16  # Limit cache size
            )
        
        
        # Run all client setups concurrently with timeout - pass parameters
        mongo_task = asyncio.create_task(setup_mongo(secrets))
        jwt_task = asyncio.create_task(setup_jwt(secrets))
        
        # Wait for all to complete with timeout
        app.state.mongoClient, app.state.jwtClient = await asyncio.wait_for(
            asyncio.gather(mongo_task, jwt_task),
            timeout=15.0  # 15 second total timeout
        )
        
        print("✅ All clients initialized successfully")

        # Setup local development auth middleware if NOT running on Lambda
        if not app.state.is_lambda:
            app.state.local_auth_middleware = create_local_dev_auth_middleware_with_secrets(env, secrets)
            print("🔧 Local development auth middleware configured with shared secrets")
        
    except asyncio.TimeoutError:
        print("❌ Client initialization timeout - some services may be unavailable")
        raise
    except Exception as e:
        print(f"❌ Error during startup: {e}")
        raise
    
    yield
    
    # Cleanup on shutdown
    try:
        if hasattr(app.state, 'mongoClient'):
            app.state.mongoClient.close()
    except Exception as e:
        print(f"Warning: Error during cleanup: {e}")


def use_route_names_as_operation_ids(application: FastAPI) -> None:
    for route in application.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        openapi_version="3.0.0",
        title="Dzgro",
        version="1.0.0",
        description="Here's a longer description of the custom **OpenAPI** schema",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    if env==ENVIRONMENT.LOCAL:
        openapi_schema["components"]["securitySchemes"] = {
            "AuthorizationHeader": {
                "type": "apiKey",
                "in": "header",
                "name": "Authorization",
            },
            "MarketplaceHeader": {
                "type": "apiKey",
                "in": "header",
                "name": "marketplace",
            },
        }

        # Apply both as global requirements (can also do per-route)
        openapi_schema["security"] = [
            {"AuthorizationHeader": []},
            {"MarketplaceHeader": []},
        ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

class ResponseFormatMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Call the actual endpoint
        response = await call_next(request)
        
        # CRITICAL: Skip middleware for OPTIONS (preflight) requests to preserve CORS
        if request.method == "OPTIONS":
            return response
            
        # For error responses or other special cases, preserve CORS headers but don't modify content
        if (response.status_code >= 400 or 
            response.status_code in [301, 302, 303, 307, 308] or
            not response.headers.get("content-type", "").startswith("application/json") or
            isinstance(response, _StreamingResponse)):
            
            # CORS headers will be handled by universal_cors_handler middleware
            return response
            
        # For regular Response objects, we need to handle this differently
        from starlette.responses import Response as StarletteResponse
        
        if not isinstance(response, StarletteResponse):
            return response
            
        # Get the response body - for regular responses it's in .body attribute
        if not (hasattr(response, 'body') and response.body):
            return response
            
        try:
            original_body = response.body.decode()
            data = json.loads(original_body)
        except (UnicodeDecodeError, json.JSONDecodeError):
            # If we can't decode or parse, return original response
            return response

        # Wrap in your standard format
        new_body = {
            "status": "success",
            "data": data
        }

        # Preserve CORS headers and remove problematic headers
        new_headers = {}
        for k, v in response.headers.items():
            key_lower = k.lower()
            # Keep CORS headers and other important headers, exclude problematic ones
            if key_lower not in ["content-length", "transfer-encoding"]:
                new_headers[k] = v

        # CORS headers will be handled by universal_cors_handler middleware

        # Return new JSONResponse with preserved headers
        return JSONResponse(
            content=new_body,
            status_code=response.status_code,
            headers=new_headers
        )



authorization_scheme = APIKeyHeader(name="Authorization", auto_error=True)
marketplace_scheme = APIKeyHeader(name="marketplace", auto_error=True)

app = FastAPI(title="FastAPI",separate_input_output_schemas=False, lifespan=lifespan, servers=[{"url": "http://localhost:8000/", "description": "Development environment"}, {"url": "https://api.dzgro.com", "description": "Production environment"}])
app.openapi = custom_openapi
origins: list[str] = ["http://localhost:4200"] if env==ENVIRONMENT.LOCAL else ["https://dev.dzgro.com","http://localhost:4200"] if env==ENVIRONMENT.DEV else ["https://staging.dzgro.com"] if env==ENVIRONMENT.STAGING else ["https://dzgro.com", "https://www.dzgro.com"]
headers: list[str] = ["Authorization","marketplaceId", "Content-Type", "Accept", "Origin", "X-Requested-With"]

# Add LocalDevAuthMiddleware first (only when NOT running on Lambda)
# Note: The middleware function is created in lifespan with shared secrets
if not is_running_on_lambda():
    @app.middleware("http")
    async def local_dev_auth_middleware(request: Request, call_next):
        # Use the middleware function created in lifespan with shared secrets
        if hasattr(app.state, 'local_auth_middleware'):
            return await app.state.local_auth_middleware(request, call_next)
        else:
            # Fallback if middleware not yet initialized
            return await call_next(request)

    print("🔧 Local development auth middleware enabled for FastAPI UI")
    print("   ↳ FastAPI UI will automatically get auth headers injected")
    print("   ↳ Swagger UI: http://127.0.0.1:8000/docs")
    print("   ↳ ReDoc: http://127.0.0.1:8000/redoc")

# Add ResponseFormatMiddleware (innermost for responses)
app.add_middleware(ResponseFormatMiddleware)

# Universal CORS handling middleware
@app.middleware("http") 
async def universal_cors_handler(request: Request, call_next):
    # Handle preflight requests immediately
    if request.method == "OPTIONS":
        origin = request.headers.get("origin", "")
        headers = {
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "Authorization, Content-Type, Accept, Origin, X-Requested-With, marketplace, marketplaceId",
            "Access-Control-Max-Age": "3600"
        }
        
        # Set origin based on allowed origins list
        if origin and origin in origins:
            headers["Access-Control-Allow-Origin"] = origin
            headers["Access-Control-Allow-Credentials"] = "true"
        else:
            # For unauthorized origins, use wildcard and no credentials
            headers["Access-Control-Allow-Origin"] = "*"
            
        return Response(status_code=200, headers=headers)
    
    # Process the request with error handling
    try:
        response = await call_next(request)
    except Exception as e:
        # If there's an unhandled exception, create an error response with CORS headers
        error_response = JSONResponse(
            status_code=500,
            content={"error": [{"errortype": "Unhandled", "code": 500, "message": str(e), "description": "An unexpected error occurred", "source": "server"}]}
        )
        
        # Add CORS headers to error response
        origin = request.headers.get("origin", "")
        if origin and origin in origins:
            error_response.headers["Access-Control-Allow-Origin"] = origin
            error_response.headers["Access-Control-Allow-Credentials"] = "true"
        else:
            # For unauthorized origins, use wildcard and no credentials
            error_response.headers["Access-Control-Allow-Origin"] = "*"
        
        error_response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        error_response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, Accept, Origin, X-Requested-With, marketplace, marketplaceId"
        
        return error_response
    
    # Add CORS headers to all responses
    origin = request.headers.get("origin", "")
    if origin and origin in origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    else:
        # For unauthorized origins, use wildcard and no credentials
        response.headers["Access-Control-Allow-Origin"] = "*"
    
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
    response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, Accept, Origin, X-Requested-With, marketplace, marketplaceId"
    
    return response

# Enhanced CORS configuration for production only (if needed as backup)
if env != ENVIRONMENT.LOCAL:
    app.add_middleware(
        CORSMiddleware, 
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"], 
        allow_headers=["*"],
        expose_headers=["*"]
    )


@app.middleware("http")
async def log_request_time(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    
    process_time_seconds = (time.perf_counter() - start_time)
    if request.method != "OPTIONS":
        if process_time_seconds > 1000:
            print(f"{request.method} {request.url.path} completed in {process_time_seconds/1000:.1f} seconds")
        else: 
            print(f"{request.method} {request.url.path} completed in {process_time_seconds:.0f} milliseconds")
    return response

# Move router imports to module level for better performance
from api.routers import (
    gstin, advertising_accounts, razorpay_orders, spapi_accounts, 
    users, marketplaces, performance_periods, performance_results, 
    state_analytics, date_analytics, products, payments, ad, 
    health, analytics, dzgro_reports, pricing
)

register_exception_handlers(app)
app.include_router(ad.router)
app.include_router(advertising_accounts.router)
app.include_router(analytics.router)
app.include_router(date_analytics.router)
app.include_router(dzgro_reports.router)
app.include_router(gstin.router)
app.include_router(health.router)
app.include_router(marketplaces.router)
app.include_router(payments.router)
app.include_router(performance_periods.router)
app.include_router(performance_results.router)
app.include_router(products.router)
app.include_router(spapi_accounts.router)
app.include_router(razorpay_orders.router)
app.include_router(state_analytics.router)
app.include_router(users.router)
app.include_router(pricing.router)

use_route_names_as_operation_ids(app)

@app.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url='/docs')

@app.get("/health")
async def health_check():
    """Simple health check endpoint that doesn't require database access"""
    return {"status": "healthy", "message": "API is running"}

@app.get("/items")
def read_items(
    authorization: str = Security(authorization_scheme),
    marketplace: str = Security(marketplace_scheme)
):
    return {"Authorization": authorization, "Marketplace": marketplace}

@app.get('/openapi.yaml', include_in_schema=False)
@functools.lru_cache()
def read_openapi_yaml() -> Response:
    openapi_json= app.openapi()
    yaml_s = io.StringIO()
    yaml.dump(openapi_json, yaml_s)
    return Response(yaml_s.getvalue(), media_type='text/yaml')
    


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="127.0.0.1", port=8000)
    





