from fastapi import Depends, FastAPI
from fastapi.responses import Response, RedirectResponse
from api.exception_handlers import register_exception_handlers
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exception_handlers import http_exception_handler,request_validation_exception_handler
from contextlib import asynccontextmanager
import functools
import io, yaml
from fastapi.openapi.utils import get_openapi


@asynccontextmanager
async def lifespan(app: FastAPI):
    from dzgrosecrets import SecretManager
    import jwt
    secrets = SecretManager()
    app.state.secrets = secrets
    jwks_url = f"https://cognito-idp.ap-south-1.amazonaws.com/{secrets.COGNITO_USER_POOL_ID}/.well-known/jwks.json"
    app.state.jwtClient = jwt.PyJWKClient(jwks_url)
    from db import DbClient
    app.state.dbClient = DbClient(secrets.MONGO_DB_CONNECT_URI)
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
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app = FastAPI(title="FastAPI",separate_input_output_schemas=False, lifespan=lifespan, servers=[{"url": "http://localhost:8000/", "description": "Development environment"}, {"url": "https://api.dzgro.com", "description": "Production environment"}])
app.openapi = custom_openapi
origins: list[str] = ["http://localhost:4200", "https://dzgro.com"]
headers: list[str] = ["Authorization","marketplaceId"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

register_exception_handlers(app)

from api.routers import user, onboarding, payments, ad, analytics,reports, product, seller,plans
app.include_router(user.router)
app.include_router(onboarding.router)
app.include_router(payments.router)
app.include_router(ad.router)
app.include_router(analytics.router)
app.include_router(product.router)
app.include_router(reports.router)
app.include_router(seller.router)
app.include_router(plans.router)

use_route_names_as_operation_ids(app)

@app.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url='/docs')

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
    





