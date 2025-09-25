"""
Test fixtures and data generators.
Centralized location for all test fixtures and mock data.
"""

from dzgroshared.db.model import Paginator, MonthDataRequest, PeriodDataRequest
from dzgroshared.db.state_analytics.model import StateRequest
from dzgroshared.db.enums import CollateType
from typing import Dict, Any, List, Optional
import random

try:
    from faker import Faker
    fake = Faker()
    HAS_FAKER = True
except ImportError:
    HAS_FAKER = False
    fake = None


class TestDataFactory:
    """Factory for generating test data."""
    
    # Constants - SINGLE SOURCE OF TRUTH
    EMAIL = "dzgrotechnologies@gmail.com"
    MARKETPLACE_ID = "6895638c452dc4315750e826"
    QUERY_ID = "686750af5ec9b6bf57fe9060"
    TEST_MONTH = "Aug 2025"
    TEST_SKU = "Mad PD Photo Portrait"
    TEST_ASIN = "B0C739QDTP"
    TEST_CATEGORY = "WALL_ART"
    TEST_PARENT_SKU = "Mad PD Single Photo-$P"
    TEST_STATE = "Karnataka"
    INVALID_STATE = "InvalidState"
    
    # Pagination defaults
    PAGINATOR_SKIP = 0
    PAGINATOR_LIMIT = 10
    
    # Default Collate Types
    DEFAULT_COLLATE_TYPE = CollateType.MARKETPLACE
    SKU_COLLATE_TYPE = CollateType.SKU
    
    @staticmethod
    def get_value_for_collate_type(collatetype: CollateType) -> str:
        """Get the appropriate test value for a given CollateType."""
        value_map = {
            CollateType.SKU: TestDataFactory.TEST_SKU,
            CollateType.ASIN: TestDataFactory.TEST_ASIN,
            CollateType.CATEGORY: TestDataFactory.TEST_CATEGORY,
            CollateType.PARENT: TestDataFactory.TEST_PARENT_SKU,
            CollateType.MARKETPLACE: TestDataFactory.MARKETPLACE_ID
        }
        return value_map.get(collatetype, "")
    
    @staticmethod
    def create_paginator(skip: int = 0, limit: int = 10) -> Paginator:
        """Create a paginator instance."""
        return Paginator(skip=skip, limit=limit)
    
    @staticmethod
    def create_month_request(
        collatetype: CollateType = CollateType.MARKETPLACE,
        value: Optional[str] = None,
        month: Optional[str] = None
    ) -> MonthDataRequest:
        """Create a month data request."""
        return MonthDataRequest(
            collatetype=collatetype,
            value=value,
            month=month or TestDataFactory.TEST_MONTH
        )
    
    @staticmethod
    def create_period_request(
        collatetype: CollateType = CollateType.MARKETPLACE,
        value: Optional[str] = None
    ) -> PeriodDataRequest:
        """Create a period data request."""
        return PeriodDataRequest(
            collatetype=collatetype,
            value=value
        )
    
    @staticmethod
    def create_state_detailed_request(
        collatetype: CollateType = CollateType.MARKETPLACE,
        value: Optional[str] = None,
        state: Optional[str] = None
    ) -> StateRequest:
        """Create a state detailed data request."""
        return StateRequest(
            collatetype=collatetype,
            value=value,
            state=state or TestDataFactory.TEST_STATE
        )
    
    @staticmethod
    def create_sku_month_request() -> MonthDataRequest:
        """Create a month request for SKU collate type."""
        return TestDataFactory.create_month_request(
            collatetype=CollateType.SKU,
            value=TestDataFactory.TEST_SKU
        )
    
    @staticmethod
    def create_sku_period_request() -> PeriodDataRequest:
        """Create a period request for SKU collate type."""
        return TestDataFactory.create_period_request(
            collatetype=CollateType.SKU,
            value=TestDataFactory.TEST_SKU
        )
    
    # Note: create_invalid_month_request removed - invalid data should be tested with raw JSON
    # to properly test API validation rather than trying to create invalid Pydantic models
    
    @staticmethod
    def create_invalid_state_request() -> StateRequest:
        """Create a state request with invalid state."""
        return TestDataFactory.create_state_detailed_request(
            state=TestDataFactory.INVALID_STATE
        )
    
    # CollateType-specific request creators
    @staticmethod
    def create_period_request_for_collate_type(collatetype: CollateType) -> PeriodDataRequest:
        """Create a period request with appropriate value for the given CollateType."""
        value = TestDataFactory.get_value_for_collate_type(collatetype) if collatetype != CollateType.MARKETPLACE else None
        return PeriodDataRequest(
            collatetype=collatetype,
            value=value
        )
    
    @staticmethod
    def create_month_request_for_collate_type(collatetype: CollateType, month: Optional[str] = None) -> MonthDataRequest:
        """Create a month request with appropriate value for the given CollateType."""
        value = TestDataFactory.get_value_for_collate_type(collatetype) if collatetype != CollateType.MARKETPLACE else None
        return MonthDataRequest(
            collatetype=collatetype,
            value=value,
            month=month or TestDataFactory.TEST_MONTH
        )
    
    @staticmethod
    def generate_random_sku() -> str:
        """Generate a random SKU for testing."""
        if HAS_FAKER and fake:
            return f"SKU-{fake.random_number(digits=6)}-{fake.random_element(elements=('A', 'B', 'C'))}"
        else:
            # Fallback without faker
            import random
            return f"SKU-{random.randint(100000, 999999)}-{random.choice(['A', 'B', 'C'])}"
    
    @staticmethod
    def generate_test_months() -> List[str]:
        """Generate list of test months."""
        return [
            "Jan 2024", "Feb 2024", "Mar 2024", "Apr 2024",
            "May 2024", "Jun 2024", "Jul 2024", "Aug 2024",
            "Sep 2024", "Oct 2024", "Nov 2024", "Dec 2024"
        ]
    
    @staticmethod
    def generate_test_states() -> List[str]:
        """Generate list of Indian states for testing."""
        return [
            "Karnataka", "Maharashtra", "Tamil Nadu", "Gujarat",
            "Rajasthan", "Uttar Pradesh", "West Bengal", "Delhi"
        ]


class MockDataGenerator:
    """Generator for mock API responses."""
    
    @staticmethod
    def mock_list_response(count: int = 5, total_count: int = 100) -> Dict[str, Any]:
        """Generate mock list response."""
        import uuid
        from datetime import datetime
        
        if HAS_FAKER and fake:
            return {
                "data": [
                    {
                        "id": fake.uuid4(),
                        "name": fake.company(),
                        "created_at": fake.date_time_this_year().isoformat()
                    }
                    for _ in range(count)
                ],
                "count": total_count
            }
        else:
            # Fallback without faker
            return {
                "data": [
                    {
                        "id": str(uuid.uuid4()),
                        "name": f"Test Company {i+1}",
                        "created_at": datetime.now().isoformat()
                    }
                    for i in range(count)
                ],
                "count": total_count
            }
    
    @staticmethod
    def mock_analytics_response() -> Dict[str, Any]:
        """Generate mock analytics response."""
        if HAS_FAKER and fake:
            return {
                "revenue": round(fake.pyfloat(left_digits=5, right_digits=2, positive=True), 2),
                "orders": fake.random_int(min=1, max=1000),
                "units_sold": fake.random_int(min=1, max=5000),
                "conversion_rate": round(fake.pyfloat(left_digits=1, right_digits=2, positive=True, max_value=100), 2)
            }
        else:
            # Fallback without faker
            import random
            return {
                "revenue": round(random.uniform(1000.0, 99999.99), 2),
                "orders": random.randint(1, 1000),
                "units_sold": random.randint(1, 5000),
                "conversion_rate": round(random.uniform(0.1, 100.0), 2)
            }
    
    @staticmethod
    def mock_error_response(message: str = "Test error") -> Dict[str, str]:
        """Generate mock error response."""
        from datetime import datetime
        
        if HAS_FAKER and fake:
            timestamp = fake.date_time_this_year().isoformat()
        else:
            timestamp = datetime.now().isoformat()
            
        return {
            "error": message,
            "timestamp": timestamp
        }