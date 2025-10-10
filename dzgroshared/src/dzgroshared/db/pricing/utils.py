from dzgroshared.db.pricing.model import PlanFeatureGroup, PlanFeature, PlanFeatureDetail, PlanName

def getFeatures()->list[PlanFeatureGroup]:

    # Feature descriptions based on name and title
    feature_descriptions = {
        ('Data Availability', 'Initial Data Sync'): 'Access to historical data when you first connect your account',
        ('Data Availability', 'Data Retention'): 'How long your data is stored and available for analysis',
        ('Payment Dashboard', 'Order Management'): 'Track and manage all your orders in one place',
        ('Payment Dashboard', 'Unpaid Order Tracking'): 'Monitor orders that have not been paid yet',
        ('Reports', 'Payment Reconciliation'): 'Reconcile payments and identify discrepancies',
        ('Reports', 'Profitability analysis'): 'Analyze profit margins across products and categories',
        ('Reports', 'Sales Forecasting'): 'Predict future sales based on historical trends',
        ('Reports', 'Inventory Planner'): 'Plan inventory levels based on demand forecasts',
        ('Analytics', 'Health Metrics'): 'Monitor key business health indicators',
        ('Analytics', 'Comparative Analysis'): 'Compare performance across different dimensions',
        ('Analytics', '5 Level Hierarchical Analysis'): 'Drill down through 5 levels of product hierarchy',
        ('Analytics', 'Month On Month Comparison'): 'Compare metrics across different months',
        ('Analytics', 'Location (State) Wise Analysis'): 'Analyze sales and performance by state',
        ('Analytics', 'Ad Performance Metrics'): 'Track advertising campaign performance',
        ('Advertising', 'Advertisement Structure Optimiser'): 'Optimize your ad campaign structure for better performance',
        ('Advertising', 'Performance Console'): 'Monitor and manage advertising performance in real-time',
        ('Advertising', 'Day Parting'): 'Schedule ads to run at specific times of day',
        ('Advertising', 'Automated Rules'): 'Set up automated rules to manage your advertising campaigns',
    }

    feature_groups = [
        {
            'title': 'Data Availability',
            'features': [
                {
                    'name': 'Initial Data Sync',
                    'hasInfo': False,
                    'paymentReconciliation': 'Last 90 Days',
                    'analytics': 'Last 60 Days',
                    'advertising': 'Last 60 Days',
                },
                {
                    'name': 'Data Retention',
                    'hasInfo': False,
                    'paymentReconciliation': 'Last 90 Days',
                    'analytics': 'Last 6 Months',
                    'advertising': 'Last 6 Months',
                },
            ],
        },
        {
            'title': 'Payment Dashboard',
            'features': [
                {
                    'name': 'Order Management',
                    'hasInfo': False,
                    'paymentReconciliation': True,
                    'analytics': True,
                    'advertising': True,
                },
                {
                    'name': 'Unpaid Order Tracking',
                    'hasInfo': False,
                    'paymentReconciliation': True,
                    'analytics': True,
                    'advertising': True,
                },
            ],
        },
        {
            'title': 'Reports',
            'features': [
                {
                    'name': 'Payment Reconciliation',
                    'hasInfo': False,
                    'paymentReconciliation': True,
                    'analytics': True,
                    'advertising': True,
                },
                {
                    'name': 'Profitability analysis',
                    'hasInfo': False,
                    'paymentReconciliation': False,
                    'analytics': True,
                    'advertising': True,
                },
                {
                    'name': 'Sales Forecasting',
                    'hasInfo': False,
                    'paymentReconciliation': False,
                    'analytics': True,
                    'advertising': True,
                },
                {
                    'name': 'Inventory Planner',
                    'hasInfo': False,
                    'paymentReconciliation': False,
                    'analytics': True,
                    'advertising': True,
                },
            ],
        },
        {
            'title': 'Analytics',
            'features': [
                {
                    'name': 'Health Metrics',
                    'hasInfo': False,
                    'paymentReconciliation': False,
                    'analytics': True,
                    'advertising': True,
                },
                {
                    'name': 'Comparative Analysis',
                    'hasInfo': False,
                    'paymentReconciliation': False,
                    'analytics': True,
                    'advertising': True,
                },
                {
                    'name': '5 Level Hierarchical Analysis',
                    'hasInfo': False,
                    'paymentReconciliation': False,
                    'analytics': True,
                    'advertising': True,
                },
                {
                    'name': 'Month On Month Comparison',
                    'hasInfo': False,
                    'paymentReconciliation': False,
                    'analytics': True,
                    'advertising': True,
                },
                {
                    'name': 'Location (State) Wise Analysis',
                    'hasInfo': False,
                    'paymentReconciliation': False,
                    'analytics': True,
                    'advertising': True,
                },
                {
                    'name': 'Ad Performance Metrics',
                    'hasInfo': False,
                    'paymentReconciliation': False,
                    'analytics': True,
                    'advertising': True,
                },
            ],
        },
        {
            'title': 'Advertising',
            'features': [
                {
                    'name': 'Advertisement Structure Optimiser',
                    'hasInfo': False,
                    'paymentReconciliation': False,
                    'analytics': False,
                    'advertising': True,
                },
                {
                    'name': 'Performance Console',
                    'hasInfo': False,
                    'paymentReconciliation': False,
                    'analytics': False,
                    'advertising': True,
                },
                {
                    'name': 'Day Parting',
                    'hasInfo': False,
                    'paymentReconciliation': False,
                    'analytics': False,
                    'advertising': True,
                },
                {
                    'name': 'Automated Rules',
                    'hasInfo': False,
                    'paymentReconciliation': False,
                    'analytics': False,
                    'advertising': True,
                },
            ],
        },
    ]

    # Transform to PlanFeatureGroup list
    result = []
    for group in feature_groups:
        transformed_features = []
        for feature in group['features']:
            # Transform hasInfo bool to info string
            info = feature_descriptions.get((group['title'], feature['name']), '')

            # Transform paymentReconciliation, analytics, advertising to list of PlanFeatureDetail
            details = [
                PlanFeatureDetail(
                    name=PlanName.PAYMENT_RECONCILIATION,
                    value=feature['paymentReconciliation']
                ),
                PlanFeatureDetail(
                    name=PlanName.ANALYTICS,
                    value=feature['analytics']
                ),
                PlanFeatureDetail(
                    name=PlanName.ADVERTISING,
                    value=feature['advertising']
                ),
            ]

            transformed_features.append(
                PlanFeature(
                    name=feature['name'],
                    info=info,
                    details=details
                )
            )

        result.append(
            PlanFeatureGroup(
                title=group['title'],
                features=transformed_features
            )
        )

    return result
