from dzgroshared.client import DzgroSharedClient
from fastapi import Depends, FastAPI, Request, Security
from fastapi.responses import Response, RedirectResponse
from api.exception_handlers import register_exception_handlers
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.security import APIKeyHeader
import io, yaml, os, functools, time, asyncio
from fastapi.openapi.utils import get_openapi
from dzgroshared.db.pricing.model import Pricing

from dotenv import load_dotenv
load_dotenv()
from dzgroshared.db.enums import ENVIRONMENT, CountryCode
env = ENVIRONMENT(os.getenv("ENV", None))
if not env: raise ValueError("ENV environment variable not set")

# Move imports to module level for better performance
from dzgroshared.secrets.client import SecretManager
from motor.motor_asyncio import AsyncIOMotorClient
from dzgroshared.razorpay.client import RazorpayClient
import jwt


def is_running_on_lambda():
    """
    Detect if the application is running on AWS Lambda
    """
    return bool(os.getenv('AWS_LAMBDA_FUNCTION_NAME')) or bool(os.getenv('LAMBDA_RUNTIME_DIR'))


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
                serverSelectionTimeoutMS=3000,  # Faster timeout for Lambda
                connectTimeoutMS=3000,  # Faster connection timeout
                socketTimeoutMS=10000,  # Socket timeout for operations
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


authorization_scheme = APIKeyHeader(name="Authorization", auto_error=True)
marketplace_scheme = APIKeyHeader(name="marketplace", auto_error=True)

app = FastAPI(title="FastAPI",separate_input_output_schemas=False, lifespan=lifespan, servers=[{"url": "http://localhost:8000/", "description": "Development environment"}, {"url": "https://api.dzgro.com", "description": "Production environment"}])
app.openapi = custom_openapi
origins: list[str] = ["http://localhost:4200", "https://dzgro.com"]
headers: list[str] = ["Authorization","marketplaceId"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.middleware("http")
async def log_request_time(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time_seconds = (time.perf_counter() - start_time)  # ms
    if request.method!="OPTIONS":
        if process_time_seconds>1:print(f"{request.method} {request.url.path} completed in {process_time_seconds:.2f} seconds")
        else: print(f"{request.method} {request.url.path} completed in {process_time_seconds*1000:.2f} milliseconds")
    return response

# Move router imports to module level for better performance
from api.routers import (
    gstin, advertising_accounts, razorpay_orders, spapi_accounts, 
    users, marketplaces, performance_periods, performance_results, 
    state_analytics, date_analytics, products, payments, ad, 
    health, analytics, dzgro_reports
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

use_route_names_as_operation_ids(app)

@app.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url='/docs')


@app.get("/items")
def read_items(
    authorization: str = Security(authorization_scheme),
    marketplace: str = Security(marketplace_scheme)
):
    return {"Authorization": authorization, "Marketplace": marketplace}

@app.get("/plans", response_model=Pricing, response_model_exclude_none=True, response_model_by_alias=False)
async def plans():
    helper = DzgroSharedClient(env)
    helper.setMongoClient(app.state.mongoClient)
    data = await helper.db.pricing.getActivePlan(CountryCode.INDIA)
    return Pricing.model_validate(data)

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
    





