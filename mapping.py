# mapping.py
"""
Maps function names to their deployment configuration, including AWS region and other metadata.
"""

DEFAULT_REGION = 'ap-south-1'  # Change this as needed
EU = 'eu-west-1'
NA = 'us-east-1'
FE = 'us-west-2'

FUNCTIONS_MAP = {
    'amazon_daily_report': {
        'region': [DEFAULT_REGION],
        'path': 'functions/amazon_daily_report',
        'description': 'Amazon Daily Report Lambda',
    },
    'dzgro_reports': {
        'region': [DEFAULT_REGION],
        'path': 'functions/dzgro_reports',
        'description': 'Dzgro Reports Lambda',
    },
    'dzgro_reports_s3_trigger': {
        'region': [DEFAULT_REGION],
        'path': 'functions/dzgro_reports_s3_trigger',
        'description': 'Dzgro Report Parquet to Excel Lambda',
    },
    'ams_change': {
        'region': [EU,NA,FE],
        'path': 'functions/ams_change',
        'description': 'AMS Change Lambda',
    },
    'ams_performance': {
        'region': [EU,NA,FE],
        'path': 'functions/ams_performance',
        'description': 'AMS Performance Lambda',
    },
    'payment_processor': {
        'region': [DEFAULT_REGION],
        'path': 'functions/payment_processor',
        'description': 'Payment Processing Lambda',
    },
    'razorpay_webhook': {
        'region': [DEFAULT_REGION],
        'path': 'functions/razorpay_webhook',
        'description': 'Razorpay Webhook Lambda',
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




