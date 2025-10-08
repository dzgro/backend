"""
Local Development Server Startup Script

This script starts the FastAPI server with environment configuration from .env file.

Usage:
    python start_local.py

The server will be available at:
- API: http://127.0.0.1:8000
- FastAPI UI (Swagger): http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

For LOCAL environment, the middleware will automatically inject:
- Authorization header (Bearer token from Cognito)
- marketplace header (from TestDataFactory.MARKETPLACE_ID)

Only for requests detected as coming from FastAPI UI.
"""

import os
import uvicorn
from dotenv import load_dotenv

if __name__ == "__main__":
    # Load environment from .env file
    load_dotenv()
    env = os.getenv("ENV")

    if not env:
        raise ValueError("ENV not set in .env file")

    print(f"🚀 Starting FastAPI server in {env.upper()} environment")
    if env == "local":
        print("🔧 LocalDevAuthMiddleware enabled for FastAPI UI auto-authentication")
        print("⚡ Optimized: Reuses secrets from lifespan context (no duplicate loading)")
    print("📖 FastAPI UI: http://127.0.0.1:8000/docs")
    print("📚 ReDoc: http://127.0.0.1:8000/redoc")
    print("🔍 API Health: http://127.0.0.1:8000/health")
    print("")

    uvicorn.run(
        "src.api.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )