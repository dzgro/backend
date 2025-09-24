"""
MongoDB Aggregation Pipeline Builder for Analytics Transformations

This module provides aggregation pipeline builders that replace the Pythonic transformations
in analytics.controller.transformData() with native MongoDB aggregation operations.

Supports all SchemaTypes:
- Period: Period-based analytics transformations
- Comparison: Comparison analytics with current vs previous periods
- Month Meters: Month meter groups transformation (legacy name: MONTH_METER_GROUPS)
- Month Bars: Month bars format transformation
- Month Data: Month data format transformation
- State Lite: Lite state analytics transformation
- State Detail: Detailed state analytics transformation
- State All: All state analytics data transformation
- Month: Monthly analytics transformation
- Month Date: Month date-based analytics transformation
- Key Metrics: Key metrics dashboard transformation

Features:
- Currency symbol support based on country code
- Automatic number formatting (K, M, B, Cr, Lacs based on locale)
- Percentage handling for appropriate metrics
- Nested metric group support up to 3 levels deep
- Reusable pipeline components for consistent transformations
"""

from bson import ObjectId
from typing import Optional
from dzgroshared.db.enums import CollateType, CountryCode, AnalyticGroupMetricLabel, AnalyticsMetric
from dzgroshared.analytics.model import (
    MONTH_METER_GROUPS, METRIC_DETAILS, MONTH_BARS, MONTH_DATA, CURRENCY_FIELDS,
    PERIOD_METRICS, COMPARISON_METRICS, STATE_LITE_METRICS, STATE_DETAILED_METRICS,
    ALL_STATE_METRICS, MONTH_METRICS, MONTH_DATE_METRICS, KEY_METRICS
)
from dzgroshared.analytics.controller import SchemaType, GroupBySchema
from dzgroshared.db.model import PeriodDataRequest, MonthDataRequest
from dzgroshared.analytics.CurrencyUtils import get_currency_symbol


class AnalyticsPipelineBuilder:
    """
    Builder class for creating MongoDB aggregation pipelines that transform analytics data
    directly in the database instead of using Python-based transformations.
    """
    
    def __init__(self, marketplace_id: ObjectId, countrycode: CountryCode = CountryCode.INDIA):
        self.marketplace_id = marketplace_id
        self.countrycode = countrycode
        
        # Cached metric details for performance
        self.percent_fields = [d.metric.value for d in METRIC_DETAILS if d.ispercentage]
        self.non_percent_fields = [d.metric.value for d in METRIC_DETAILS if not d.ispercentage]
        self.currency_fields = [d.metric.value for d in METRIC_DETAILS if d.isCurrency]
        
        # Currency symbol from centralized utility
        self.currency_symbol = get_currency_symbol(countrycode)
    
    def _create_format_number_expression(self, field_path: str, metric: AnalyticsMetric) -> dict:
        """
        Create MongoDB expression for formatting numbers based on metric type and country.
        
        Args:
            field_path: MongoDB field path (e.g., "$data.revenue")
            metric: The analytics metric to format
            
        Returns:
            MongoDB expression for formatting the number
        """
        
        is_percent = metric.value in self.percent_fields
        is_currency = metric.value in self.currency_fields
        is_currency = metric.value in self.currency_fields
        
        if is_percent:
            # Format percentage fields as "X.XX%"
            return {
                "$concat": [
                    {
                        "$toString": {
                            "$round": [
                                {"$ifNull": [field_path, 0]}, 
                                2
                            ]
                        }
                    },
                    "%"
                ]
            }
        else:
            # Format non-percentage fields with appropriate suffixes based on magnitude
            abs_val_expr = {"$abs": {"$ifNull": [field_path, 0]}}
            
            # Base formatting without currency
            if self.countrycode == CountryCode.INDIA:
                # Indian number system: Lacs, Crores
                base_format = {
                    "$switch": {
                        "branches": [
                            {
                                "case": {"$gte": [abs_val_expr, 10000000]},  # >= 1 Cr (10M)
                                "then": {
                                    "$concat": [
                                        {
                                            "$toString": {
                                                "$round": [
                                                    {"$divide": [abs_val_expr, 10000000]}, 
                                                    2
                                                ]
                                            }
                                        },
                                        " Cr"
                                    ]
                                }
                            },
                            {
                                "case": {"$gte": [abs_val_expr, 100000]},  # >= 1 Lac (100K)
                                "then": {
                                    "$concat": [
                                        {
                                            "$toString": {
                                                "$round": [
                                                    {"$divide": [abs_val_expr, 100000]}, 
                                                    2
                                                ]
                                            }
                                        },
                                        " Lacs"
                                    ]
                                }
                            },
                            {
                                "case": {"$gte": [abs_val_expr, 1000]},  # >= 1K
                                "then": {
                                    "$concat": [
                                        {
                                            "$toString": {
                                                "$round": [
                                                    {"$divide": [abs_val_expr, 1000]}, 
                                                    2
                                                ]
                                            }
                                        },
                                        " K"
                                    ]
                                }
                            }
                        ],
                        "default": {
                            "$toString": {
                                "$round": [
                                    {"$ifNull": [field_path, 0]}, 
                                    1
                                ]
                            }
                        }
                    }
                }
            else:
                # International number system: M, B
                base_format = {
                    "$switch": {
                        "branches": [
                            {
                                "case": {"$gte": [abs_val_expr, 1000000000]},  # >= 1B
                                "then": {
                                    "$concat": [
                                        {
                                            "$toString": {
                                                "$round": [
                                                    {"$divide": [abs_val_expr, 1000000000]}, 
                                                    2
                                                ]
                                            }
                                        },
                                        " B"
                                    ]
                                }
                            },
                            {
                                "case": {"$gte": [abs_val_expr, 1000000]},  # >= 1M
                                "then": {
                                    "$concat": [
                                        {
                                            "$toString": {
                                                "$round": [
                                                    {"$divide": [abs_val_expr, 1000000]}, 
                                                    2
                                                ]
                                            }
                                        },
                                        " M"
                                    ]
                                }
                            },
                            {
                                "case": {"$gte": [abs_val_expr, 1000]},  # >= 1K
                                "then": {
                                    "$concat": [
                                        {
                                            "$toString": {
                                                "$round": [
                                                    {"$divide": [abs_val_expr, 1000]}, 
                                                    2
                                                ]
                                            }
                                        },
                                        " K"
                                    ]
                                }
                            }
                        ],
                        "default": {
                            "$toString": {
                                "$round": [
                                    {"$ifNull": [field_path, 0]}, 
                                    1
                                ]
                            }
                        }
                    }
                }
            
            # Add currency symbol if this is a currency field
            if is_currency:
                return {
                    "$concat": [
                        self.currency_symbol,
                        base_format
                    ]
                }
            else:
                return base_format
    
    def _create_generic_metric_items(self, group_schema, data_field_prefix: str = "data") -> list[dict]:
        """
        Generic method to create items array for any metric group based on schema definition.
        
        Args:
            group_schema: MetricGroup schema definition
            data_field_prefix: Prefix for data fields (e.g., "data", "$data")
            
        Returns:
            List of item dictionaries for the metric group
        """
        items = []
        
        for item in group_schema.items:
            metric_field = f"{data_field_prefix}.{item.metric.value}"
            
            # Get metric details for label and description
            metric_detail = next((d for d in METRIC_DETAILS if d.metric == item.metric), None)
            
            item_dict = {
                "label": item.label or (metric_detail.label if metric_detail else item.metric.value),
                "value": {
                    "$round": [
                        {"$ifNull": [f"${metric_field}", 0]}, 
                        2
                    ]
                },
                "valueString": self._create_format_number_expression(f"${metric_field}", item.metric)
            }
            
            # Add description if available
            if metric_detail and metric_detail.description:
                item_dict["description"] = metric_detail.description
            
            # Handle nested items recursively
            if item.items:
                item_dict["items"] = []
                for nested_item in item.items:
                    nested_metric_field = f"{data_field_prefix}.{nested_item.metric.value}"
                    nested_metric_detail = next((d for d in METRIC_DETAILS if d.metric == nested_item.metric), None)
                    
                    nested_item_dict = {
                        "label": nested_item.label or (nested_metric_detail.label if nested_metric_detail else nested_item.metric.value),
                        "value": {
                            "$round": [
                                {"$ifNull": [f"${nested_metric_field}", 0]}, 
                                2
                            ]
                        },
                        "valueString": self._create_format_number_expression(f"${nested_metric_field}", nested_item.metric)
                    }
                    
                    if nested_metric_detail and nested_metric_detail.description:
                        nested_item_dict["description"] = nested_metric_detail.description
                    
                    # Handle deeply nested items
                    if nested_item.items:
                        nested_item_dict["items"] = []
                        for deep_nested_item in nested_item.items:
                            deep_nested_metric_field = f"{data_field_prefix}.{deep_nested_item.metric.value}"
                            deep_nested_metric_detail = next((d for d in METRIC_DETAILS if d.metric == deep_nested_item.metric), None)
                            
                            deep_nested_item_dict = {
                                "label": deep_nested_item.label or (deep_nested_metric_detail.label if deep_nested_metric_detail else deep_nested_item.metric.value),
                                "value": {
                                    "$round": [
                                        {"$ifNull": [f"${deep_nested_metric_field}", 0]}, 
                                        2
                                    ]
                                },
                                "valueString": self._create_format_number_expression(f"${deep_nested_metric_field}", deep_nested_item.metric)
                            }
                            
                            if deep_nested_metric_detail and deep_nested_metric_detail.description:
                                deep_nested_item_dict["description"] = deep_nested_metric_detail.description
                            
                            nested_item_dict["items"].append(deep_nested_item_dict)
                    
                    item_dict["items"].append(nested_item_dict)
            
            items.append(item_dict)
        
        return items

    def _create_meter_group_items(self, group_schema, data_field_prefix: str = "data") -> list[dict]:
        """
        Create items array for a meter group based on schema definition.
        Legacy method that delegates to the generic implementation.
        """
        return self._create_generic_metric_items(group_schema, data_field_prefix)
    
    
    
    def create_month_data_pipeline(self, data_field: str = "data") -> list[dict]:
        """
        Create pipeline stages to transform data into MONTH_DATA format.
        
        Args:
            data_field: Name of the field containing the analytics data
            
        Returns:
            List of MongoDB aggregation pipeline stages for data transformation
        """
        
        # MONTH_DATA is a single MetricGroup with key metrics for general display
        data_items = self._create_meter_group_items(MONTH_DATA, data_field)
        
        data_dict = {
            "label": MONTH_DATA.metric.value,
            "items": data_items
        }
        
        return [
            {
                "$addFields": {
                    "data": data_dict
                }
            },
            {
                "$project": {
                    "data": 1,
                    "month": 1,
                    "period": 1,
                    "_id": 0
                }
            }
        ]
    
    
    

    
    def get_complete_month_lite_data_pipeline(self, req: PeriodDataRequest) -> list[dict]:
        """
        Create a complete pipeline for getMonthLiteData that includes all transformations.
        This replaces all transformData calls and creates a complete MonthDataResponse structure.
        
        Args:
            req: Period data request
            
        Returns:
            Complete aggregation pipeline that produces MonthDataResponse-compatible results
        """

        def create_complete_month_data_response_pipeline(data_field: str = "data") -> list[dict]:
            """
            Create pipeline stages to transform data into complete MonthDataResponse format.
            This creates all three components: data, bars, and meterGroups.
            
            Args:
                data_field: Name of the field containing the analytics data
                
            Returns:
                Pipeline stages that create complete MonthDataResponse structure
            """
            
            # Create meter groups
            meter_groups = []
            for group_schema in MONTH_METER_GROUPS:
                group_dict = {
                    "label": group_schema.metric.value,
                    "items": self._create_meter_group_items(group_schema, data_field)
                }
                meter_groups.append(group_dict)
            
            # Create bars (single group)
            bars_dict = {
                "label": MONTH_BARS.metric.value,
                "items": self._create_meter_group_items(MONTH_BARS, data_field)
            }
            
            # Create data (single group)
            data_dict = {
                "label": MONTH_DATA.metric.value,
                "items": self._create_meter_group_items(MONTH_DATA, data_field)
            }
            
            return [
                {
                    "$addFields": {
                        "meterGroups": meter_groups,
                        "bars": bars_dict,
                        "data": data_dict
                    }
                },
                {
                    "$project": {
                        "month": 1,
                        "period": 1,
                        "data": 1,
                        "bars": 1,
                        "meterGroups": 1,
                        "_id": 0
                    }
                }
            ]
        
        from dzgroshared.db.date_analytics.pipelines import GetMonthsLiteData
        base_pipeline = GetMonthsLiteData.pipeline(self.marketplace_id, req)
        # Add complete month data response transformation
        complete_transformation_stages = create_complete_month_data_response_pipeline("data")
        base_pipeline.extend(complete_transformation_stages)
        
        return base_pipeline

    def get_period_pipeline(self, req: PeriodDataRequest) -> list[dict]:

        def create_period_pipeline(data_field: str = "data") -> list[dict]:
            """
            Create pipeline stages to transform data into Period format.
            This mimics the transformPeriodData function from controller.py.
            """
            period_groups = []
            
            for group_schema in PERIOD_METRICS:
                group_dict = {
                    "label": group_schema.metric.value,
                    "items": self._create_generic_metric_items(group_schema, data_field)
                }
                period_groups.append(group_dict)
            
            return [
                {
                    "$addFields": {
                        "data": period_groups
                    }
                },
            ]
        
        from dzgroshared.db.date_analytics.pipelines import GetPeriodAnalytics
        pipeline = GetPeriodAnalytics.pipeline(self.marketplace_id, req)
        return pipeline+create_period_pipeline()
    
    def get_comparison_pipeline(self, req: PeriodDataRequest) -> list[dict]:

        def create_comparison_pipeline(data_field: str = "data") -> list[dict]:
            """
            Create pipeline stages to transform data into Comparison format.
            This mimics the transformComparisonData function from controller.py.
            """
            comparison_groups = []
            
            for group_schema in COMPARISON_METRICS:
                group_dict = {
                    "label": group_schema.metric.value,
                    "items": self._create_generic_metric_items(group_schema, data_field)
                }
                comparison_groups.append(group_dict)
            
            return [ { "$addFields": { "data": comparison_groups } } ]
        
        from dzgroshared.db.performance_period_results.pipelines import GetPerformanceResultsForAllTags
        pipeline = GetPerformanceResultsForAllTags.pipeline(self.marketplace_id, req)
        return pipeline+create_comparison_pipeline()

    def get_state_lite_pipeline(self, req: MonthDataRequest) -> list[dict]:
        def create_state_lite_pipeline(data_field: str = "data") -> list[dict]:
            """
            Create pipeline stages to transform data into State Lite format.
            """
            state_groups = []
            
            for group_schema in STATE_LITE_METRICS:
                group_dict = {
                    "label": group_schema.metric.value,
                    "items": self._create_generic_metric_items(group_schema, data_field)
                }
                state_groups.append(group_dict)
            
            return [ { "$addFields": { "data": state_groups } } ]
        
        from dzgroshared.db.state_analytics.pipelines import GetStatesDataForMonth
        pipeline = GetStatesDataForMonth.pipeline(self.marketplace_id, req)
        return pipeline+create_state_lite_pipeline()
    
    def create_state_detail_pipeline(self, data_field: str = "data") -> list[dict]:
        """
        Create pipeline stages to transform data into State Detail format.
        """
        state_groups = []
        
        for group_schema in STATE_DETAILED_METRICS:
            group_dict = {
                "label": group_schema.metric.value,
                "items": self._create_generic_metric_items(group_schema, data_field)
            }
            state_groups.append(group_dict)
        
        return [
            {
                "$addFields": {
                    "data": state_groups
                }
            },
            {
                "$project": {
                    "data": 1,
                    "state": 1,
                    "_id": 0
                }
            }
        ]

    def get_state_all_pipeline(self, req: MonthDataRequest) -> list[dict]:
        def create_state_all_pipeline(data_field: str = "data") -> list[dict]:
            """
            Create pipeline stages to transform data into State All format.
            This mimics the transformStateAllData function.
            """
            # Extract all metrics from all state schema groups
            all_metrics = []
            for group_schema in ALL_STATE_METRICS:
                for item in group_schema.items:
                    all_metrics.append(item.metric)
                    if item.items:
                        for nested_item in item.items:
                            all_metrics.append(nested_item.metric)
                            if nested_item.items:
                                for deep_nested_item in nested_item.items:
                                    all_metrics.append(deep_nested_item.metric)
            
            # Create values array with formatted values for each metric
            values_array = []
            for metric in all_metrics:
                metric_field = f"{data_field}.{metric.value}"
                values_array.append({
                    "value": {
                        "$round": [
                            {"$ifNull": [f"${metric_field}", 0]}, 
                            2
                        ]
                    },
                    "valueString": self._create_format_number_expression(f"${metric_field}", metric)
                })
            
            return [ { "$addFields": { "values": values_array } }]
        
        from dzgroshared.db.state_analytics.pipelines import GetStatesDataForMonth
        pipeline = GetStatesDataForMonth.pipeline(self.marketplace_id, req)
        return pipeline+create_state_all_pipeline()
    
    def create_month_pipeline(self, data_field: str = "data") -> list[dict]:
        """
        Create pipeline stages to transform data into Month format.
        This mimics the transformSchemaData function for Month schema.
        """
        month_groups = []
        
        for group_schema in MONTH_METRICS:
            group_dict = {
                "label": group_schema.metric.value,
                "items": self._create_generic_metric_items(group_schema, data_field)
            }
            month_groups.append(group_dict)
        
        return [
            {
                "$addFields": {
                    "data": month_groups
                }
            },
            {
                "$project": {
                    "data": 1,
                    "_id": 0
                }
            }
        ]
    
    def create_month_date_pipeline(self, data_field: str = "data") -> list[dict]:
        """
        Create pipeline stages to transform data into Month Date format.
        This mimics the transformMonthDateData function.
        """
        # Extract all metrics from month date schema groups
        all_metrics = []
        for group_schema in MONTH_DATE_METRICS:
            for item in group_schema.items:
                all_metrics.append(item.metric)
        
        # Create values array with formatted values for each metric
        values_array = []
        for metric in all_metrics:
            metric_field = f"{data_field}.{metric.value}"
            values_array.append({
                "value": {
                    "$round": [
                        {"$ifNull": [f"${metric_field}", 0]}, 
                        2
                    ]
                },
                "valueString": self._create_format_number_expression(f"${metric_field}", metric)
            })
        
        return [
            {
                "$addFields": {
                    "values": values_array
                }
            },
            {
                "$project": {
                    "date": 1,
                    "values": 1,
                    "_id": 0
                }
            }
        ]
    
    def create_key_metrics_pipeline(self, data_field: str = "data") -> list[dict]:
        """
        Create pipeline stages to transform data into Key Metrics format.
        This mimics the transformKeyMetrics function.
        """
        key_metric_groups = []
        
        for group_schema in KEY_METRICS:
            items = []
            for item in group_schema.items:
                metric_detail = next((d for d in METRIC_DETAILS if d.metric == item.metric), None)
                
                item_dict = {
                    "metric": item.metric.value,
                    "label": metric_detail.label if metric_detail else item.metric.value,
                    # Key metrics have special structure with last30Days, months, performance, periods
                    # For pipeline transformation, we'll create a simplified version
                    "last30Days": {
                        "values": [],  # Would be populated from actual data
                        "labels": []
                    },
                    "months": [],
                    "performance": [],
                    "periods": []
                }
                items.append(item_dict)
            
            group_dict = {
                "metric": group_schema.metric.value,
                "items": items
            }
            key_metric_groups.append(group_dict)
        
        return [
            {
                "$addFields": {
                    "data": key_metric_groups
                }
            },
            {
                "$project": {
                    "data": 1,
                    "_id": 0
                }
            }
        ]