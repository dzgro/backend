# SAM-App Project Structure

This repository contains multiple interconnected Poetry projects that together form the Dzgro AWS serverless application ecosystem.

## Projects Overview

### 1. **api** - Main Lambda Function Handler
The core FastAPI application that serves as the primary Lambda function handler for the Dzgro platform.

**Key Features:**
- FastAPI-based REST API with routing, middleware, and exception handling
- JWT authentication and authorization using PyJWT and cryptography
- Supports multiple routers for different business domains
- Integrates with dzgroshared for database, storage, and AWS services
- Uses Mangum adapter for AWS Lambda integration
- Environment-based configuration via python-dotenv

**Tech Stack:** FastAPI 0.111.0, Uvicorn, PyJWT, Mangum

### 2. **dzgroshared** - Shared Library & Utilities
A comprehensive shared library providing reusable components across all projects.

**Core Modules:**
- **Database:** MongoDB models, schemas, and enums (using Motor/PyMongo)
- **AWS Integration:** S3 storage, SQS queues, Cognito authentication clients
- **External APIs:** Amazon SP-API, Razorpay payment gateway
- **Analytics:** Business intelligence and reporting utilities
- **Functions:** Common business logic and helper functions
- **Client:** HTTP client wrapper with retry logic (using httpx + backoff)

**Tech Stack:** Pydantic 2.11.7, Boto3, Motor 3.7.1, PyMongo, HTTPX

### 3. **sam-deploy** - Optimized AWS SAM Deployment
Modern deployment automation system using AWS SAM with Lambda aliases and HTTP API stage variables.

**Key Features:**
- **Multi-region deployment:** Supports 4 AWS regions (ap-south-1, eu-west-1, us-east-1, us-west-2)
- **Deployment options:**
  - Core Product Features (all resources, all regions)
  - AMS Features (AMS Lambdas/queues only, multi-region)
  - Staging/Production promotions (Lambda alias updates with OTP verification)
- **Resource optimization:** Single Lambda with aliases, single HTTP API with stage variables
- **Layer management:** Build once, reuse across regions with caching
- **Certificate automation:** ACM certificate creation via boto3
- **Security:** OTP-protected promotions via AWS SES

**Architecture Benefits:**
- 50-75% reduction in Lambda functions
- 67% reduction in API Gateways
- Simplified version management with Lambda aliases
- Cost-effective HTTP API vs REST API

**Tech Stack:** Boto3, Pydantic, PyYAML, Inquirer, AWS SAM CLI

### 4. **secrets** - Secrets Management
Centralized secrets management package for accessing AWS Secrets Manager and environment variables.

**Purpose:**
- Provides unified interface for retrieving secrets
- Supports multiple environments (local, dev, staging, prod)
- Used as a dependency by api and dzgroshared projects

**Tech Stack:** Python 3.12+

### 5. **tests** - Comprehensive Test Suite
Professional test infrastructure with isolated Poetry environment for end-to-end testing.

**Test Coverage:**
- **Integration tests:** Full-stack API endpoint testing with authentication
- **Analytics tests:** Date analytics, state analytics, data aggregation
- **Account management:** Marketplace, selling accounts, advertising accounts
- **Test helpers:** Centralized fixtures, assertions, and data factories

**Features:**
- Separate Poetry project with independent dependencies
- Parallel test execution with pytest-xdist
- Coverage reporting with pytest-cov
- Centralized test data management via TestDataFactory
- CI/CD ready with GitHub Actions integration

**Tech Stack:** Pytest 8.4.2, HTTPX, Faker, pytest-asyncio

### 6. **utilities** - Standalone Utility Scripts
Collection of independent utility scripts for various tasks.

**Current Utilities:**
- **make_mask_square:** Image processing utility for mask manipulation

## Project Dependencies

```
api
  - depends on: dzgroshared, secrets
  - deployed by: sam-deploy

dzgroshared
  - depends on: secrets
  - used by: api, tests, sam-deploy

secrets
  - used by: api, dzgroshared

tests
  - depends on: api, dzgroshared
  - tests: api, dzgroshared modules

sam-deploy
  - depends on: dzgroshared (for enums/models)
  - deploys: api Lambda functions, infrastructure
```

## Development Workflow

1. **Local Development:**
   - Use `api/start_local.py` to run FastAPI locally
   - Configure environment via `.env` file

2. **Testing:**
   - Navigate to `tests/` and run `poetry run pytest`
   - Use integration tests for end-to-end validation
   - Coverage reports available via pytest-cov

3. **Deployment:**
   - Navigate to `sam-deploy/` and run `poetry run python -m sam_deploy`
   - Select deployment type (Core Product, AMS Features, or Promotions)
   - OTP verification required for staging/production promotions

4. **Secrets Management:**
   - Add secrets to AWS Secrets Manager
   - Access via `secrets` package across all projects

## Key Technologies

- **Language:** Python 3.12+
- **Package Manager:** Poetry
- **Web Framework:** FastAPI
- **Database:** MongoDB (Motor/PyMongo)
- **Cloud Provider:** AWS (Lambda, S3, SQS, Cognito, API Gateway, ACM)
- **IaC:** AWS SAM (Serverless Application Model)
- **Testing:** Pytest with async support
- **External APIs:** Amazon SP-API, Razorpay

## Repository Structure

```
sam-app/
  - api/                 # Main Lambda function (FastAPI)
  - dzgroshared/         # Shared library
  - sam-deploy/          # Deployment automation
  - secrets/             # Secrets management
  - tests/               # Test suite
  - utilities/           # Standalone utilities
  - .env                 # Environment configuration
  - .gitignore           # Git ignore rules
  - README.md            # Project documentation
```

## Notes

- Each subdirectory is an independent Poetry project
- All projects require Python 3.12 or higher
- Deployment managed exclusively through `sam-deploy` project
- Shared code centralized in `dzgroshared` to avoid duplication
