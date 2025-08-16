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
        'routes': [
            {
                'method': 'POST',
                'path': '/webhook/rzrpay',
                'destination': 'SQS',
                'headers': ['x-razorpay-event-id', 'X-Razorpay-Signature']
            }
        ]
    },
    'AmazonReports': {
        'region': [DEFAULT_REGION],
        'description': 'Amazon Daily Reports',
        'function': 'AmazonDailyReport'
    },
    'AmsChange': {
        'region': [EU, NA, FE],
        'description': 'AMSChange',
    },
    'AmsPerformance': {
        'region': [EU, NA, FE],
        'description': 'AMSPerformance',
    },
    'Payment': {
        'region': [DEFAULT_REGION],
        'description': 'Payment Processing',
        'function': 'PaymentProcessor'
    }
}

def createPolicy(region:str, name:str, arns: list[str]):

    return {
        "Type": "AWS::SQS::QueuePolicy",
        "Properties": {
            "Queues": [
                {'Ref': f'{name}Q'}
            ],
            "PolicyDocument": {
                "Version": "2008-10-17",
                "Id": f'Id-{name}-{region}',
                "Statement": [
                    {
                        "Sid": f'Sid-{name}-{region}',
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "sns.amazonaws.com"
                        },
                        "Action": "SQS:SendMessage",
                        "Resource": {'Fn::GetAtt': [f'{name}Q', 'Arn']},
                        "Condition": {
                            "ArnEquals": {"aws:SourceArn": arns}
                        }
                    },
                    {
                    "Sid": f'SidReview-{name}-{region}',
                    "Effect": "Allow",
                    "Principal": {
                            "AWS": "arn:aws:iam::926844853897:role/ReviewerRole"
                        },
                    "Action": "SQS:GetQueueAttributes",
                    "Resource": "*"
                    }
                ]
            }
        }
    }



def getAMSPerformancePolicy(region: str):
    if region == 'us-east-1':
        ids = ['906013806264', '802324068763', '370941301809', '877712924581', '709476672186', '154357381721']
    elif region == 'eu-west-1':
        ids = ['668473351658', '562877083794', '947153514089', '664093967423', '623198756881', '195770945541']
    elif region == 'us-west-2':
        ids = ['074266271188', '622939981599', '310605068565', '818973306977', '485899199471', '112347756703']
    return createPolicy(region, "AmsPerformance", [f"arn:aws:sns:{region}:{id}:*" for id in ids])

def getAMSChangeSetPolicy(region: str):
    if region == 'us-east-1':
        ids = ['570159413969', '118846437111', '305370293182', '644124924521']
    elif region == 'eu-west-1':
        ids = ['834862128520', '130948361130', '648558082147', '503759481754']
    elif region == 'us-west-2':
        ids = ['527383333093', '668585072850', '802070757281', '248074939493']
    return createPolicy(region, "AmsChange", [f"arn:aws:sns:{region}:{id}:*" for id in ids])



