import time
from fastapi import Depends, FastAPI, Request, Security
from fastapi.responses import Response, RedirectResponse
from api.exception_handlers import register_exception_handlers
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exception_handlers import http_exception_handler,request_validation_exception_handler
from contextlib import asynccontextmanager
import functools
from fastapi.security import APIKeyHeader
import io, yaml, os
from fastapi.openapi.utils import get_openapi
from dotenv import load_dotenv
load_dotenv()
from dzgroshared.models.enums import ENVIRONMENT
env = ENVIRONMENT(os.getenv("ENV", None))
if not env: raise ValueError("ENV environment variable not set")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.env = env
    from dzgroshared.secrets.client import SecretManager
    app.state.secrets = SecretManager(app.state.env).secrets
    from motor.motor_asyncio import AsyncIOMotorClient
    app.state.mongoClient = AsyncIOMotorClient(app.state.secrets.MONGO_DB_CONNECT_URI, appname="dzgro-api")
    from dzgroshared.razorpay.client import RazorpayClient
    app.state.razorpayClient = RazorpayClient(app.state.secrets.RAZORPAY_CLIENT_ID, app.state.secrets.RAZORPAY_CLIENT_SECRET)
    import jwt
    jwks_url = f"https://cognito-idp.ap-south-1.amazonaws.com/{app.state.secrets.COGNITO_USER_POOL_ID}/.well-known/jwks.json"
    app.state.jwtClient = jwt.PyJWKClient(jwks_url)
    yield


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

register_exception_handlers(app)

from api.routers import user, payments, ad, analytics,reports, product, marketplaces,plans, spapi, adv_account, gstin, pg_orders
app.include_router(spapi.router)
app.include_router(adv_account.router)
app.include_router(user.router)
app.include_router(payments.router)
app.include_router(ad.router)
app.include_router(analytics.router)
app.include_router(product.router)
app.include_router(reports.router)
app.include_router(marketplaces.router)
app.include_router(plans.router)
app.include_router(gstin.router)
app.include_router(pg_orders.router)

use_route_names_as_operation_ids(app)

@app.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url='/docs')


@app.get("/items/")
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
    





