# SAM-App Test Suite

This is a **dedicated test project** for the sam-app ecosystem, providing comprehensive testing capabilities across all modules. It's designed as a separate Poetry project with isolated dependencies and professional testing infrastructure.

## 🎯 Project Overview

The SAM-App Test Suite provides end-to-end testing for:

- **API Module**: FastAPI endpoints, authentication, request/response validation
- **Analytics Module**: Date analytics, state analytics, data aggregation
- **Account Management**: Marketplace, selling accounts, advertising accounts
- **DzgroShared Module**: Shared utilities, database models, client operations

## 🚀 Quick Start

```bash
# 1. Navigate to tests directory
cd tests

# 2. Install dependencies (creates isolated environment)
poetry install

# 3. Run all tests
poetry run pytest

# 4. Run tests with coverage
poetry run pytest --cov=src --cov-report=html
```

## 📁 Project Structure

```
sam-app/tests/                     # Dedicated test project root
├── 📄 pyproject.toml              # Poetry configuration & dependencies
├── 📄 shared_fixtures.py          # 🎯 SINGLE SOURCE for all pytest fixtures
├── 📄 pytest.ini                 # Legacy pytest config (migrated to pyproject.toml)
├── 📄 README.md                   # This documentation
├── 📄 poetry.lock                 # Dependency lock file
│
├── 📂 src/test_helpers/           # 🛠️ Centralized test utilities
│   ├── 📄 __init__.py
│   ├── 📄 assertions.py           # Response validation helpers
│   └── 📄 fixtures.py             # 🔧 TestDataFactory - SINGLE SOURCE OF TRUTH
│
└── 📂 integration/                # 🔗 Full-stack API integration tests
    ├── 📄 conftest.py            # 🔗 Simple import from shared_fixtures.py
    ├── 📂 test_analytics/        # Analytics router tests
    │   ├── 📄 test_date_analytics.py    # /analytics/dates/* endpoints
    │   └── 📄 test_state_analytics.py   # /states/* endpoints
    └── 📂 test_accounts/         # Account management tests
        ├── 📄 test_marketplace.py       # /marketplace/* endpoints
        ├── 📄 test_selling_account.py   # /selling-account/* endpoints
        └── 📄 test_advertising_account.py # /advertising-account/* endpoints
```

## 🏗️ Architecture Principles

### **Clean Test Structure (Updated!)**

The test structure has been simplified and optimized:

- **`shared_fixtures.py`**: 🎯 Single location for all pytest fixtures
- **`src/test_helpers/fixtures.py`**: 🔧 `TestDataFactory` - single source of truth for all constants
- **`integration/conftest.py`** & **`unit/conftest.py`**: Simple imports from shared fixtures
- **No duplication**: Eliminated confusing multiple `conftest.py` files

### **Separation of Concerns**

- **Integration Tests**: Test complete API workflows with authentication, database, and external services
- **Test Helpers**: Reusable utilities to eliminate code duplication
- **Centralized Fixtures**: Single source of truth for all test data and configuration

### **Centralized Configuration**

- All hardcoded values (emails, IDs, test data) centralized in `TestDataFactory` class
- Shared fixtures available across all test files via `shared_fixtures.py`
- Consistent assertion helpers for response validation

### **Isolated Environment**

- Separate Poetry project with independent dependencies
- No interference with main application dependencies
- Professional CI/CD ready configuration

## ⚙️ Setup & Installation

### Prerequisites

- Python 3.12+ (matches main project)
- Poetry package manager
- Access to MongoDB instance (for integration tests)
- Valid AWS Cognito credentials (for authentication tests)

### Installation Options

#### Option 1: Poetry Environment (Recommended) 🌟

```bash
# Navigate to tests directory
cd tests

# Install Poetry if not already available
pip install poetry

# Install all dependencies in isolated environment
poetry install

# Verify installation
poetry run pytest --version
```

#### Option 2: Development Environment

```bash
cd tests

# Install dev dependencies (includes optional performance tools)
poetry install --with performance

# This includes: locust, pytest-benchmark for load testing
```

#### Option 3: Quick Setup (Not Recommended)

```bash
cd tests
pip install pytest pytest-asyncio pytest-cov httpx faker
# Note: May conflict with main project dependencies
```

### Environment Configuration

#### Required Environment Variables

```bash
# MongoDB connection
export MONGO_URI="mongodb://localhost:27017"

# AWS Cognito (for authentication tests)
export COGNITO_USER_POOL_ID="your_pool_id"
export COGNITO_APP_CLIENT_ID="your_client_id"

# Test environment
export TEST_ENV="local"
```

#### Configuration Files

- **Test Data**: Edit `TestConfig` class in `conftest.py`
- **Pytest Settings**: Configured in `pyproject.toml` under `[tool.pytest.ini_options]`
- **Coverage Settings**: Configured in `pyproject.toml` under `[tool.coverage.*]`

## Test Categories

### Integration Tests (`integration/`)

- **Purpose**: Test API endpoints end-to-end with full application stack
- **Scope**: FastAPI routes, authentication, database integration, business logic
- **Location**: `integration/test_analytics/`, `integration/test_accounts/`
- **Markers**: `@pytest.mark.integration`

## 🧪 Running Tests

### Basic Test Execution

```bash
# Run all tests
poetry run pytest

# Run with verbose output
poetry run pytest -v

# Run with short traceback (easier to read)
poetry run pytest --tb=short

# Stop on first failure
poetry run pytest -x
```

### Test Categories & Organization

```bash
# 🔗 Integration tests (API endpoints with full stack)
poetry run pytest integration/

# 📊 Analytics tests specifically
poetry run pytest integration/test_analytics/

# 🏪 Account management tests
poetry run pytest integration/test_accounts/

# 📄 Specific test file
poetry run pytest integration/test_analytics/test_date_analytics.py

# 🎯 Specific test function
poetry run pytest integration/test_analytics/test_date_analytics.py::test_get_monthly_data_table
```

### Advanced Test Selection

```bash
# 🏷️ Run by markers
poetry run pytest -m integration          # Integration tests only
poetry run pytest -m "api and not slow"   # API tests, exclude slow ones
poetry run pytest -m marketplaces         # Marketplace functionality

# 🔍 Run by keyword matching
poetry run pytest -k "analytics"          # Tests with 'analytics' in name
poetry run pytest -k "list and not malformed"  # List tests, exclude malformed JSON
```

### Performance & Debugging

```bash
# 🚀 Parallel execution (faster)
poetry run pytest -n auto                 # Auto-detect CPU cores
poetry run pytest -n 4                    # Use 4 parallel processes

# 📊 Coverage reporting
poetry run pytest --cov=src --cov-report=html        # HTML report
poetry run pytest --cov=src --cov-report=term-missing # Terminal with missing lines
poetry run pytest --cov=src --cov-report=xml         # XML for CI/CD

# 🐛 Debugging options
poetry run pytest --pdb                   # Drop into debugger on failure
poetry run pytest --lf                    # Run last failed tests only
poetry run pytest --ff                    # Run failed tests first
poetry run pytest --durations=10          # Show 10 slowest tests
```

### Test Results & Reports

```bash
# 📋 Generate detailed reports
poetry run pytest --html=report.html --self-contained-html
poetry run pytest --junitxml=results.xml

# 📈 Performance benchmarking (if installed)
poetry run pytest --benchmark-only
```

## ⚙️ Configuration & Customization

### 🎛️ Test Data Configuration

All hardcoded test values are centralized in the `TestDataFactory` class (`src/test_helpers/fixtures.py`):

```python
class TestDataFactory:
    """Factory for generating test data - SINGLE SOURCE OF TRUTH"""

    # Constants
    EMAIL = "dzgrotechnologies@gmail.com"
    MARKETPLACE_ID = "6895638c452dc4315750e826"
    QUERY_ID = "686750af5ec9b6bf57fe9060"
    TEST_MONTH = "Dec 2024"
    TEST_SKU = "TEST-SKU-123"
    TEST_STATE = "Karnataka"

    # Pagination defaults
    PAGINATOR_SKIP = 0
    PAGINATOR_LIMIT = 10

    # Factory methods
    @staticmethod
    def create_month_request():
        return MonthDataRequest(...)

    @staticmethod
    def create_paginator():
        return Paginator(skip=0, limit=10)
```

**💡 Best Practice**: Edit these values in `TestDataFactory` to affect all tests globally.

### 🛠️ Test Helpers & Utils

#### Assertion Helpers (`src/test_helpers/assertions.py`)

```python
assert_ok_response(resp)                    # Validates 200 status
assert_list_response(resp, key, label, paginator)  # Validates paginated lists
assert_analytics_response(resp)             # Validates analytics data
assert_concurrent_requests_success(resps)   # Validates parallel requests
```

#### Data Factories (`src/test_helpers/fixtures.py`)

```python
TestDataFactory.create_month_request()      # Generate month data requests
TestDataFactory.create_paginator()          # Generate pagination objects
MockDataGenerator.mock_list_response()      # Generate mock API responses
```

### 🏷️ Test Markers

Configure test execution with markers:

```python
@pytest.mark.integration    # Integration test
@pytest.mark.unit          # Unit test
@pytest.mark.slow          # Long-running test
@pytest.mark.api           # API-related test
@pytest.mark.marketplaces  # Marketplace functionality
```

### 📊 Coverage Configuration

Coverage settings in `pyproject.toml`:

```toml
[tool.coverage.run]
source = ["src"]
omit = ["*/tests/*", "*/__pycache__/*"]

[tool.coverage.report]
exclude_lines = ["pragma: no cover", "def __repr__"]
```

## 🎯 Best Practices & Guidelines

### 📂 Test Organization

#### **Directory Structure**

- `integration/` → API endpoint tests with full stack
- `unit/` → Isolated function/class tests
- Group related functionality in subdirectories
- Use clear, descriptive file names

#### **Naming Conventions**

```python
# ✅ Good: Descriptive and specific
test_marketplace_list_with_pagination()
test_date_analytics_invalid_month_format()
test_concurrent_requests_handle_rate_limiting()

# ❌ Avoid: Vague or generic
test_api()
test_data()
test_function()
```

### 🏭 Test Data Management

#### **Use Centralized Factories**

```python
# ✅ Good: Use factories
request = TestDataFactory.create_month_request(
    collatetype=CollateType.SKU,
    value=TestDataFactory.TEST_SKU
)

# ❌ Avoid: Hardcoded data in tests
request = MonthDataRequest(
    collatetype=CollateType.SKU,
    value="TEST-SKU-123",  # Hardcoded!
    month="Dec 2024"
)
```

#### **Configuration Management**

- Edit `TestDataFactory` class in `src/test_helpers/fixtures.py` for global changes
- Use environment variables for sensitive data
- Mock external services with `MockDataGenerator`

### 🔍 Assertion Strategies

#### **Use Helper Functions**

```python
# ✅ Good: Use standardized helpers
data = assert_analytics_response(resp)
assert_list_response(resp, 'data', 'Marketplaces', paginator)

# ❌ Avoid: Duplicate assertion logic
assert resp.status_code == 200
assert 'data' in resp.json()
# ... repeated validation logic
```

#### **Test Structure Pattern**

```python
@pytest.mark.asyncio
async def test_feature_scenario(client: AsyncClient, fixture: Model):
    """Test description explaining what this validates"""
    # Arrange: Set up test data
    request_data = TestDataFactory.create_request()

    # Act: Execute the operation
    resp = await client.post("/endpoint", json=request_data.model_dump())

    # Assert: Validate results
    data = assert_analytics_response(resp)
    assert len(data) > 0
```

### ⚡ Performance Optimization

#### **Fixture Scope Management**

```python
@pytest.fixture(scope="session")  # Expensive setup once
def auth_token(): ...

@pytest.fixture(scope="function")  # Fresh data per test
def test_data(): ...
```

#### **Parallel Execution**

- Use `pytest -n auto` for CPU-bound tests
- Mark database tests appropriately for isolation
- Use `@pytest.mark.slow` for long-running tests

### 🚨 Error Handling & Edge Cases

#### **Comprehensive Test Coverage**

```python
# Test happy path
async def test_endpoint_success(): ...

# Test error conditions
async def test_endpoint_invalid_data(): ...
async def test_endpoint_missing_auth(): ...
async def test_endpoint_malformed_json(): ...

# Test edge cases
async def test_endpoint_empty_response(): ...
async def test_endpoint_large_payload(): ...
async def test_endpoint_concurrent_requests(): ...
```

## 🔄 Migration & Legacy Support

### Current Status

#### ✅ **Migrated Components**

- **Analytics Tests**: Fully migrated to `integration/test_analytics/`
- **Account Tests**: Migrated to `integration/test_accounts/`
- **Test Helpers**: Centralized in `src/test_helpers/`
- **Configuration**: Unified in `TestConfig` class

#### 🔄 **Legacy Components**

- **`test_bed.py`**: Original parametrized tests (preserved for compatibility)
- **Old fixtures**: Some still in root `conftest.py` with `_legacy` suffix

### Migration Checklist

When migrating old tests:

```bash
# 1. Move test file to appropriate directory
mv test_feature.py integration/test_feature/

# 2. Update imports to use centralized helpers
# Replace:
from .conftest import assert_ok_response
# With:
from src.test_helpers.assertions import assert_ok_response

# 3. Use TestDataFactory for hardcoded values
# Replace:
email = "test@example.com"
# With:
email = TestDataFactory.EMAIL

# 4. Remove duplicate helper functions
# Delete local assert_* functions, use centralized ones
```

### Backward Compatibility

The migration preserves backward compatibility:

- Old test files continue to work
- Legacy fixtures available with `_legacy` suffix
- Gradual migration path without breaking existing tests

## 📦 Dependencies & Tools

### 🧪 Core Testing Framework

```toml
pytest = "^8.4.2"              # Main testing framework
pytest-asyncio = "^1.1.0"      # Async/await test support
httpx = "0.28.1"               # HTTP client for API testing
faker = "^19.0.0"              # Test data generation
```

### 📊 Enhanced Testing Features

```toml
pytest-cov = "^4.0.0"         # Coverage reporting & analysis
pytest-xdist = "^3.0.0"       # Parallel test execution
pytest-mock = "^3.12.0"       # Advanced mocking utilities
```

### 🏗️ Project Dependencies

```toml
# Local development dependencies
api = { path = "../api", develop = true }           # FastAPI application
dzgroshared = { path = "../dzgroshared", develop = true }  # Shared utilities
```

### ⚡ Performance Testing (Optional)

```toml
# Install with: poetry install --with performance
locust = "^2.16.0"            # Load testing framework
pytest-benchmark = "^4.0.0"   # Performance benchmarking
```

### 🛠️ Development Tools

#### **Available Commands**

```bash
# Package management
poetry show                    # List installed packages
poetry update                  # Update dependencies
poetry add <package>           # Add new dependency

# Environment management
poetry shell                   # Activate virtual environment
poetry env info               # Show environment details
```

#### **IDE Integration**

- **VS Code**: Python extension auto-detects Poetry environment
- **PyCharm**: Configure interpreter to Poetry environment
- **Vim/Neovim**: Use Poetry shell or configure LSP

## 🚀 CI/CD Integration

### GitHub Actions Workflow

Create `.github/workflows/tests.yml`:

```yaml
name: "🧪 Test Suite"
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.12"]

    steps:
      - name: "📥 Checkout code"
        uses: actions/checkout@v4

      - name: "🐍 Setup Python ${{ matrix.python-version }}"
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: "📦 Install Poetry"
        uses: snok/install-poetry@v1
        with:
          version: latest
          virtualenvs-create: true
          virtualenvs-in-project: true

      - name: "🔧 Install dependencies"
        working-directory: ./tests
        run: poetry install

      - name: "🧪 Run tests with coverage"
        working-directory: ./tests
        run: |
          poetry run pytest \
            --cov=src \
            --cov-report=xml \
            --cov-report=term-missing \
            --junitxml=test-results.xml

      - name: "📊 Upload coverage to Codecov"
        uses: codecov/codecov-action@v3
        with:
          file: ./tests/coverage.xml
          fail_ci_if_error: true

      - name: "📋 Upload test results"
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: test-results
          path: ./tests/test-results.xml
```

### Pre-commit Hooks

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: "🧪 Run tests"
        entry: bash -c 'cd tests && poetry run pytest'
        language: system
        pass_filenames: false
        always_run: true
```

### Docker Integration

Create `tests/Dockerfile.test`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app/tests

# Install Poetry
RUN pip install poetry

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev

# Copy test files
COPY . .

# Run tests
CMD ["poetry", "run", "pytest", "--cov=src", "--cov-report=xml"]
```

## 🎯 Project Benefits

This professional test structure provides:

### ✅ **Development Benefits**

- **Isolated Environment**: No dependency conflicts with main application
- **Fast Feedback**: Parallel execution and selective test running
- **Maintainable Code**: Centralized configuration and reusable helpers
- **Professional Standards**: Industry-standard testing practices

### ✅ **Team Benefits**

- **Clear Organization**: Easy to find and understand test structure
- **Consistent Patterns**: Standardized test writing approach
- **Documentation**: Comprehensive README and inline documentation
- **Onboarding**: New developers can quickly understand and contribute

### ✅ **DevOps Benefits**

- **CI/CD Ready**: Professional pipeline integration
- **Coverage Reporting**: Automated test coverage analysis
- **Scalable Architecture**: Easy to add new test categories
- **Cross-module Testing**: Validate interactions between components

---

## 📞 Support & Contributing

### Getting Help

- **Issues**: Check existing test failures and patterns
- **Documentation**: This README covers most common scenarios
- **Code Examples**: Look at existing tests for patterns

### Contributing Guidelines

1. **Follow Naming Conventions**: Use descriptive test names
2. **Use Centralized Helpers**: Don't duplicate assertion logic
3. **Update Configuration**: Add new test values to `TestConfig`
4. **Write Documentation**: Comment complex test scenarios
5. **Test Your Tests**: Ensure new tests actually validate the intended behavior

---

**🎉 Happy Testing!** This structure provides a solid foundation for comprehensive, maintainable, and professional testing of the SAM-App ecosystem.
