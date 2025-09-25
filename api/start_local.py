"""
Local Development Server Startup Script

This script starts the FastAPI server in local development mode with 
the LocalDevAuthMiddleware enabled for automatic authentication in FastAPI UI.

Usage:
    python start_local.py

The server will be available at:
- API: http://127.0.0.1:8000
- FastAPI UI (Swagger): http://127.0.0.1:8000/docs  
- ReDoc: http://127.0.0.1:8000/redoc

The middleware will automatically inject:
- Authorization header (Bearer token from Cognito)
- marketplace header (from TestDataFactory.MARKETPLACE_ID)

Only for requests detected as coming from FastAPI UI.
"""

import os
import uvicorn

if __name__ == "__main__":
    # Set environment to local
    os.environ["ENV"] = "local"
    
    print("🚀 Starting FastAPI server in LOCAL development mode")
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