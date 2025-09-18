from mangum import Mangum
from api import main

def lambda_handler(event, context):
    """
    Lambda handler that strips /api prefix from API Gateway requests
    before passing to Mangum/FastAPI
    """
    # Strip /api prefix from path if present
    if event.get("path") and event["path"].startswith("/api"):
        event["path"] = event["path"][4:]  # Remove '/api'
        
    # Also handle rawPath if it exists (for API Gateway v2)
    if event.get("rawPath") and event["rawPath"].startswith("/api"):
        event["rawPath"] = event["rawPath"][4:]  # Remove '/api'
    
    # Handle pathParameters proxy value
    if event.get("pathParameters") and event["pathParameters"].get("proxy"):
        # The proxy value should not include the /api prefix
        proxy_value = event["pathParameters"]["proxy"]
        # Ensure the path matches the proxy value
        if not event.get("path"):
            event["path"] = "/" + proxy_value
    
    # Initialize Mangum handler with lifespan enabled for your startup logic
    mangum_handler = Mangum(main.app, lifespan="on")
    
    # Pass the modified event to Mangum
    return mangum_handler(event, context)

# Set the handler for Lambda
handler = lambda_handler