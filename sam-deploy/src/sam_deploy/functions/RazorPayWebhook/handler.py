"""
RazorPay Webhook Handler

Handles webhook events from Razorpay payment gateway.
Routes: /webhook/rzrpay/{event_type}

Example routes:
- /webhook/rzrpay/order/paid
- /webhook/rzrpay/invoice/paid
- /webhook/rzrpay/invoice/expired
"""

def handler(event, context):
    """
    Lambda handler for Razorpay webhook events.

    Args:
        event: HTTP API Gateway event (payload format 2.0)
        context: Lambda context

    Returns:
        HTTP response with status code and body
    """
    # Extract path from event
    raw_path = event.get('rawPath', '')
    path_parameters = event.get('pathParameters', {})
    proxy = path_parameters.get('proxy', '')

    # Extract headers
    headers = event.get('headers', {})
    razorpay_signature = headers.get('x-razorpay-signature', '')
    razorpay_event_id = headers.get('x-razorpay-event-id', '')

    # Extract body
    body = event.get('body', '')

    # Log the webhook event
    print(f"Received webhook event:")
    print(f"  Path: {raw_path}")
    print(f"  Proxy: {proxy}")
    print(f"  Razorpay Signature: {razorpay_signature[:20]}..." if razorpay_signature else "  No signature")
    print(f"  Razorpay Event ID: {razorpay_event_id}")
    print(f"  Body length: {len(body)} bytes")

    # TODO: Process the webhook event based on the proxy path
    # Example:
    # if proxy == 'order/paid':
    #     handle_order_paid(body, razorpay_signature, razorpay_event_id)
    # elif proxy == 'invoice/paid':
    #     handle_invoice_paid(body, razorpay_signature, razorpay_event_id)
    # elif proxy == 'invoice/expired':
    #     handle_invoice_expired(body, razorpay_signature, razorpay_event_id)

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': '{"status": "webhook received"}'
    }
