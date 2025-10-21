# FastAPI Local Development Authentication

This middleware provides automatic authentication for FastAPI's interactive documentation (Swagger UI/ReDoc) when running in local development mode.

## 🎯 Purpose

FastAPI's built-in documentation UI is extremely useful for testing APIs, but it requires manual entry of authentication headers. This middleware detects requests from the FastAPI UI and automatically injects the required headers:

- **Authorization**: Bearer token obtained from AWS Cognito
- **marketplace**: Marketplace ID from test configuration

## 🚀 Usage

### Starting the Server

```bash
# Option 1: Use the provided startup script
cd api
python start_local.py

# Option 2: Manual startup with environment variable
cd api
ENV=local poetry run uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload
```

### Using FastAPI UI

1. Start the server (it will automatically enable the middleware in LOCAL mode)
2. Open http://127.0.0.1:8000/docs in your browser
3. The middleware will automatically detect FastAPI UI requests and inject auth headers
4. Test your APIs without manually entering headers! 🎉

## 🔍 How It Works

### Detection Logic

The middleware identifies FastAPI UI requests using multiple methods:

1. **Direct Documentation Pages**: `/docs`, `/redoc`, `/openapi.json`
2. **Referer Header**: Requests with referer containing `/docs` or `/redoc`
3. **User-Agent Patterns**: Swagger UI, OpenAPI, ReDoc user agents
4. **Request Characteristics**: JSON requests without existing auth headers

### Authentication Flow

1. **Token Generation**: Uses the same Cognito authentication as tests

   - Email: From `TestDataFactory.EMAIL`
   - Password: From secrets (`USER_DUMMY_PASSWORD`)
   - Caches tokens for 1 hour to avoid repeated API calls

2. **Header Injection**: Automatically adds headers to matching requests
   - `Authorization: Bearer <token>`
   - `marketplace: <marketplace_id>`

### Safety Features

- **Environment Gated**: Only active when `ENV=local`
- **Request Filtering**: Only affects FastAPI UI requests, not external API calls
- **Error Handling**: Logs errors but doesn't break the request flow
- **Caching**: Reuses tokens to minimize Cognito API calls

## 📁 Files

- `local_dev_auth.py`: Main middleware implementation
- `start_local.py`: Convenient startup script
- `README.md`: This documentation

## 🛠️ Configuration

The middleware uses the same configuration as your tests:

```python
# From TestDataFactory (tests/src/test_helpers/fixtures.py)
EMAIL = "dzgrotechnologies@gmail.com"
MARKETPLACE_ID = "6895638c452dc4315750e826"

# From secrets (via SecretManager)
COGNITO_USER_POOL_ID
COGNITO_APP_CLIENT_ID
USER_DUMMY_PASSWORD
```

## 🔧 Integration

The middleware is automatically configured in the FastAPI `lifespan` context for optimal performance:

```python
# In lifespan context (main.py)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ... load secrets once ...
    secrets = await asyncio.to_thread(get_secrets_from_env_or_ssm, env)

    # Setup local development auth middleware with shared secrets
    if env == ENVIRONMENT.DEV:
        app.state.local_auth_middleware = create_local_dev_auth_middleware_with_secrets(env, secrets)
        print("🔧 Local development auth middleware configured with shared secrets")

# Middleware registration uses the pre-configured function
if env == ENVIRONMENT.DEV:
    @app.middleware("http")
    async def local_dev_auth_middleware(request: Request, call_next):
        if hasattr(app.state, 'local_auth_middleware'):
            return await app.state.local_auth_middleware(request, call_next)
        else:
            return await call_next(request)
```

### � Performance Optimization

- **Shared Secrets**: Reuses secrets loaded in lifespan, avoiding duplicate SSM/environment variable reads
- **Token Caching**: Caches Cognito tokens for 1 hour to minimize API calls
- **Lazy Loading**: Only loads test constants when first needed
- **Single Setup**: Configuration happens once during app startup

## 🚨 Important Notes

- **Local Only**: This middleware is designed for development and should never run in production
- **Test Dependencies**: Uses the same authentication constants as your test suite
- **Network Dependency**: Requires internet access to reach AWS Cognito
- **Caching**: Tokens are cached for 1 hour to improve performance

## 🎉 Benefits

- ✅ **No Manual Headers**: FastAPI UI works without entering auth headers
- ✅ **Real Authentication**: Uses actual Cognito tokens, not mocks
- ✅ **Transparent**: Doesn't affect other requests or external API clients
- ✅ **Development Speed**: Faster API testing and development workflow
- ✅ **Same as Tests**: Uses identical auth flow as your test suite

Enjoy seamless API development! 🚀
