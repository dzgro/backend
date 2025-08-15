# mapping.py
"""
Maps function names to their deployment configuration, including AWS region and other metadata.
"""

DEFAULT_REGION = 'ap-south-1'  # Change this as needed
EU = 'eu-west-1'
NA = 'us-east-1'
FE = 'us-west-2'

FUNCTIONS_MAP = {
    'AmazonDailyReport': {
        'region': [DEFAULT_REGION],
        'path': 'functions/AmazonDailyReport',
        'description': 'Amazon Daily Report Lambda',
    },
    'DzgroReports': {
        'region': [DEFAULT_REGION],
        'path': 'functions/DzgroReports',
        'description': 'Dzgro Reports Lambda',
    },
    'DzgroReportsS3Trigger': {
        'region': [DEFAULT_REGION],
        'path': 'functions/DzgroReportsS3Trigger',
        'description': 'Dzgro Report Parquet to Excel Lambda',
    },
    'AmsChange': {
        'region': [EU, NA, FE],
        'path': 'functions/AmsChange',
        'description': 'AMS Change Lambda',
    },
    'AmsPerformance': {
        'region': [EU, NA, FE],
        'path': 'functions/AmsPerformance',
        'description': 'AMS Performance Lambda',
    },
    'PaymentProcessor': {
        'region': [DEFAULT_REGION],
        'path': 'functions/PaymentProcessor',
        'description': 'Payment Processing Lambda',
    },
    'RazorpayWebhookProcessor': {
        'region': [DEFAULT_REGION],
        'path': 'functions/RazorpayWebhookProcessor',
        'description': 'Razorpay Webhook Processor Lambda',
    },
}

QUEUES_MAP = {
    'RazorpayWebhook': {
        'region': [DEFAULT_REGION],
        'description': 'Main Queue for Razorpay Webhook',
        'function': 'razorpay_webhook'
    },
    'AmazonReports': {
        'region': [DEFAULT_REGION],
        'description': 'Amazon Daily Reports',
        'function': 'amazon_daily_report'
    },
    'AmsChange': {
        'region': [EU, NA, FE],
        'description': 'AMS Change',
    },
    'AmsPerformance': {
        'region': [EU, NA, FE],
        'description': 'AMS Performance',
    },
    'Payment': {
        'region': [DEFAULT_REGION],
        'description': 'Payment Processing',
        'function': 'payment_processor'
    }
}




