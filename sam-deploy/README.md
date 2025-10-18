# SAM Deploy - Optimized AWS Deployment Project

## Overview

This is a **standalone, independent** AWS SAM deployment project that implements an optimized deployment strategy using Lambda aliases and HTTP API stage variables. This project is designed to replace the existing `deploy` project with a more efficient architecture that reduces resource proliferation.

## ⚠️ CRITICAL CONSTRAINTS & INDEPENDENCE

**This project is COMPLETELY INDEPENDENT and self-contained.**

### What You CANNOT Change:
- **NO modifications** to any other projects (`deploy/`, `api/`, `dzgroshared/`, etc.)
- **NO changes** to existing Lambda function code
- **NO changes** to external libraries or shared dependencies
- **NO references** to the `deploy/` project in code (it will be deleted after migration)

### What You CAN Customize:
- **FULL freedom** to customize the mapping file (`src/sam_deploy/config/mapping.py`)
  - Create NEW Pydantic models as needed
  - Redesign the configuration structure
  - Change property names, validation rules, etc.
- **ONLY restriction on mapping**: Cannot change models imported from external libraries (`dzgroshared`, `pydantic`, etc.)
  - Example: Can use `ENVIRONMENT` enum from `dzgroshared.db.enums` but cannot modify it
  - Example: Can use Pydantic's `BaseModel` but cannot change Pydantic's behavior

### Project Independence:
- Creates its own CloudFormation stack (separate from `deploy` project)
- Contains **COMPLETE copies** of critical files (SAM executor, layer builder, etc.)
- **NO runtime dependencies** on `deploy/` project
- Can be deployed alongside existing infrastructure for gradual migration
- After migration, the `deploy/` project will be **DELETED**

## Background & Motivation

**NEW ARCHITECTURE (Current):**
This project creates **separate, independent CloudFormation stacks** for each environment:
- **3 complete stacks**: dev, staging, prod
- Each stack has its own: Lambda functions, HTTP APIs, SQS queues, S3 buckets, Cognito pools
- **No dependencies between environments** - each is completely isolated
- Stack names: `dzgro-sam-dev`, `dzgro-sam-staging`, `dzgro-sam-prod`

**Previous Approach (Old Deploy Project):**
- Same as above but without SAM optimization
- Used REST API instead of HTTP API
- Less efficient resource management

**This Project's Goals:**
1. Deploy all three environments (dev, staging, prod) independently
2. Use SAM for optimized deployment and management
3. Create separate HTTP APIs with proper CORS configuration per environment
4. Enable complete isolation between environments
5. Simplify infrastructure using modern SAM features

## Regional Deployment Strategy

This project supports **TWO deployment types** with different resource configurations across **ALL REGIONS**:

### 🌏 Core Product Features (ALL Regions - Full Deployment)
When selecting **Core Product Features**, the system deploys **ALL resources to ALL regions**:

**Resources deployed to ALL regions (ap-south-1, eu-west-1, us-east-1, us-west-2):**
- ✅ All Lambda functions (Api, QueueModelMessageProcessor, CognitoTrigger, DzgroReportsS3Trigger, AmsChange, AmsPerformance)
- ✅ All HTTP APIs (/api/{proxy+}, /webhook)
- ✅ All SQS Queues (for all queue types including AMS queues)
- ✅ All S3 Buckets (all bucket types)
- ✅ Cognito User Pools
- ✅ Certificates (Auth, API, Webhook)
- ✅ Common Lambda Layers (shared across all regions)

**Primary Region (ap-south-1 - Mumbai, India):**
- This is the main region for core operations
- All resources deployed here first

**Secondary Regions (eu-west-1, us-east-1, us-west-2):**
- Same resources deployed sequentially
- Layers built once and reused

### 🔌 AMS Features (ALL Regions - AMS-Only Deployment)
When selecting **AMS Features**, the system deploys **ONLY AMS components to ALL regions**:

**Resources deployed to ALL regions (ap-south-1, eu-west-1, us-east-1, us-west-2):**
- ✅ AMS-specific Lambdas (AmsChange, AmsPerformance)
- ✅ AMS-specific SQS Queues (AMS_CHANGE, AMS_PERFORMANCE)
- ✅ Common Lambda Layers (shared from first region build)
- ❌ NO HTTP APIs
- ❌ NO S3 Buckets
- ❌ NO Cognito
- ❌ NO Certificates (except for ap-south-1 if needed)
- ❌ NO Core Product Lambdas

### Interactive Deployment Selection

When running the deployment, users are prompted with **FOUR options**:

```
Select deployment type:
1. Core Product Features (All Regions)
   Deploys: All APIs, Lambdas, Queues, Buckets, Cognito, Certificates
   Regions: ap-south-1, eu-west-1, us-east-1, us-west-2 (sequential)
   Auto-publishes to DEV alias

2. AMS Features (All Regions)
   Deploys: AMS Lambdas and Queues only
   Regions: ap-south-1, eu-west-1, us-east-1, us-west-2 (sequential)

3. Deploy to Staging 🔒 (Requires OTP)
   Promotes Lambda versions from DEV to STAGING alias
   Applies to: All regions
   Secure operation with email OTP verification

4. Deploy to Production 🔒 (Requires OTP)
   Promotes Lambda versions from STAGING to PROD alias
   Applies to: All regions
   Secure operation with email OTP verification
```

**Selection Details:**

**Option 1: Core Product Features**
- Deploys to **ALL FOUR regions sequentially**: ap-south-1, eu-west-1, us-east-1, us-west-2
- Creates ALL resources (APIs, Lambdas, Queues, Buckets, Cognito, etc.)
- Builds and caches Lambda layers (used by all regions)
- Each region deployment is **sequential** (SAM CLI limitation)
- **Auto-publishes to DEV** alias

**Option 2: AMS Features**
- Deploys to **ALL FOUR regions sequentially**: ap-south-1, eu-west-1, us-east-1, us-west-2
- Each region deployment is **sequential** (SAM CLI limitation)
- Reuses layers built in first region (significant time savings)
- Only creates AMS-specific resources per region

**Option 3: Deploy to Staging** 🔒
- **Promotes Lambda alias versions** (not a full deployment)
- Updates STAGING alias to point to latest DEV version
- Applies to **ALL Lambdas** in the system
- **Secure workflow**:
  1. Confirmation prompt with version details
  2. OTP sent to `dzgrotechnologies@gmail.com` via SES
  3. User enters OTP
  4. Alias updated only if OTP matches
- No new infrastructure created
- Instant promotion (seconds, not minutes)

**Option 4: Deploy to Production** 🔒
- **Promotes Lambda alias versions** (not a full deployment)
- Updates PROD alias to point to latest STAGING version
- Applies to **ALL Lambdas** in the system
- **Secure workflow** (same as Staging):
  1. Confirmation prompt with version details
  2. OTP sent to `dzgrotechnologies@gmail.com` via SES
  3. User enters OTP
  4. Alias updated only if OTP matches
- No new infrastructure created
- Instant promotion (seconds, not minutes)

### Lambda Alias Promotion Workflow (Staging & Production)

**DEV → STAGING → PROD Promotion Flow:**

```
DEV (Auto-published)
  ↓ [Option 3: Deploy to Staging] 🔒 OTP Required
STAGING
  ↓ [Option 4: Deploy to Production] 🔒 OTP Required
PROD
```

**Secure Promotion Process:**

Each promotion (Staging or Production) follows this **secure workflow**:

```python
# Step 1: Show current state and confirmation
print("\n🚨 CRITICAL OPERATION: Lambda Alias Promotion")
print(f"Target Environment: {target_env.upper()}")
print(f"\nLambdas to be promoted:")
for lambda_name in all_lambdas:
    current_version = get_alias_version(lambda_name, source_alias)
    print(f"  - {lambda_name}: Version {current_version} → {target_alias}")

confirm = input("\n⚠️  Proceed with promotion? (yes/no): ")
if confirm.lower() != "yes":
    print("❌ Promotion cancelled")
    return

# Step 2: Send OTP via SES
otp = generate_random_otp()  # 6-digit random OTP
send_otp_via_ses(otp, "dzgrotechnologies@gmail.com")
print(f"\n📧 OTP sent to dzgrotechnologies@gmail.com")

# Step 3: Verify OTP
user_otp = input("Enter OTP: ")
if user_otp != otp:
    print("❌ Invalid OTP. Promotion aborted.")
    return

# Step 4: Update all Lambda aliases
print("\n⚡ Updating Lambda aliases...")
for lambda_name in all_lambdas:
    update_lambda_alias(lambda_name, target_alias, source_version)
    print(f"  ✅ {lambda_name}: {target_alias} → Version {source_version}")

print(f"\n✅ All lambdas promoted to {target_env.upper()} successfully!")
```

**OTP Implementation via SES:**

```python
import boto3
import random

def generate_random_otp() -> str:
    """Generate 6-digit random OTP"""
    return str(random.randint(100000, 999999))

def send_otp_via_ses(otp: str, recipient: str):
    """Send OTP via AWS SES"""
    ses = boto3.client('ses', region_name='ap-south-1')

    subject = f"🔒 SAM Deploy: Lambda Promotion OTP"
    body = f"""
    Lambda Alias Promotion OTP

    Your One-Time Password (OTP) for Lambda alias promotion:

    {otp}

    This OTP is valid for this session only.
    Do not share this code with anyone.

    If you did not initiate this deployment, please ignore this email.
    """

    ses.send_email(
        Source='noreply@dzgro.com',  # Verified SES email
        Destination={'ToAddresses': [recipient]},
        Message={
            'Subject': {'Data': subject},
            'Body': {'Text': {'Data': body}}
        }
    )
```

### Layer Sharing Across Regions

**Common layers are built ONCE** and reused:

```python
# Deployment flow for AMS Features (Option 2)
1. Build common layers (pymongo, etc.) - ONCE
2. Deploy to eu-west-1 (AMS Lambdas + Queues) - uses cached layers
3. Deploy to us-east-1 (AMS Lambdas + Queues) - uses cached layers
4. Deploy to us-west-2 (AMS Lambdas + Queues) - uses cached layers
```

**Layer Build Strategy:**
- Layers are built during FIRST region deployment
- Cached locally for reuse in subsequent regions
- Dramatically reduces deployment time for multi-region
- Layer ARNs are region-specific but content is identical

## New Optimization Strategy

### Key Changes from Original Deploy Project

#### 1. **S3 Buckets** (No Change)
- **Strategy**: Continue creating 4 buckets per environment
- **Reason**: Environment-specific data isolation is critical
- **Resources Created**: 4 buckets � N bucket types = Multiple environment-specific buckets
- **Naming**: Uses `getBucketName()` helper - keeps existing pattern

#### 2. **SQS Queues** (Modified)
- **Strategy**: Create 4 queues per queue type (now includes LOCAL)
- **New Addition**: LOCAL environment queues created but NOT triggered by Lambda
- **Resources Created**:
  - Main Queue (Q) � 4 environments
  - Dead Letter Queue (DLQ) � 4 environments
- **Naming**: Uses `getQueueName()` helper with type suffix (Q, DLQ, EventSourceMapping)

#### 3. **Lambda Functions** (Major Change)
- **Strategy**: Create 1 Lambda function with aliases for each environment
- **Aliases**: dev, staging, prod (LOCAL excluded from aliases)
- **Auto-publish**: DEV environment auto-publishes new versions
- **Resources Created**:
  - 1 Lambda function per function type
  - 3 Lambda aliases (dev, staging, prod)
- **Naming**: Base function name uses `getFunctionName()` without environment suffix
- **Helper Functions**: `getLambdaRoleName()` becomes environment-agnostic

#### 4. **HTTP APIs** (Major Change)
- **Strategy**: Use single HTTP API (not REST API) with stage variables for both API and webhook routes
- **Resources Created**:
  - 1 HTTP API with both `/api/{proxy+}` and `/webhook/rzrpay/{proxy+}` routes (with API certificate)
- **Stage Variables**: Point to appropriate Lambda alias based on stage (dev/staging/prod)
- **Stages**: dev, staging, prod (LOCAL excluded)
- **Integration**:
  - `/api/{proxy+}`: Routes to Api Lambda function via stage variables
  - `/webhook/rzrpay/{proxy+}`: Routes to RazorPayWebhook Lambda function directly
- **CORS Configuration**:
  - **Single HTTP API with wildcard CORS**:
    - AllowOrigin: `*` (wildcard to support both API and external webhooks)
    - AllowMethods: GET, POST, PUT, DELETE, PATCH
    - AllowHeaders: Content-Type, Authorization, Marketplace, X-Razorpay-Signature, x-razorpay-event-id
    - Supports both secure API access and external webhook calls
- **Route Details**:
  - `/api/{proxy+}`: Main application API
    - Integration: Lambda proxy to Api function with alias routing
    - Methods: ANY (all HTTP methods)
  - `/webhook/rzrpay/{proxy+}`: Razorpay webhook endpoint
    - Integration: Lambda proxy to RazorPayWebhook function (direct, no queue)
    - Method: POST only
    - Headers: X-Razorpay-Signature, x-razorpay-event-id

#### 5. **Cognito User Pools** (No Change)
- **Strategy**: Continue creating 3 Cognito User Pools
- **Environments**: dev, staging, prod (LOCAL excluded)
- **Naming**: Uses `getUserPoolName()` helper - keeps existing pattern

#### 6. **Certificate Management** (Modified)
- **Strategy**: Use ACM certificates via **boto3** (NOT SAM)
- **Why boto3**:
  - Cognito requires certificates in us-east-1 (different region)
  - HTTP API needs valid ARN before deployment (SAM creates during deployment, causing chicken-egg problem)
- **Types**:
  - Auth certificates (us-east-1) - for Cognito
  - API certificates (region-specific) - for single HTTP API (both `/api` and `/webhook` routes)
- **Resources Created**:
  - 1 Auth certificate (us-east-1)
  - 1 API certificate (per region) - now handles both API and webhook routes
- **Custom Domains**:
  - **For dev/staging**:
    - Auth: `auth.{env}.dzgro.com`
    - API: `api.{env}.dzgro.com` (handles both `/api` and `/webhook` routes)
  - **For prod** (no env suffix):
    - Auth: `auth.dzgro.com`
    - API: `api.dzgro.com` (handles both `/api` and `/webhook` routes)
- **Helper**: `getWildCardCertificateArn()` - supports 'Auth' and 'Api' types
- **Reference**: See `Builder.py` deploy function for boto3 certificate creation logic

## Architecture Comparison

### Before (Original Deploy)
```
Environment: DEV
   Lambda: ApiFunctionDev
   Lambda: QueueModelMessageProcessorFunctionDev
   API Gateway: ApiGatewayDev
   SQS: AmazonReportsQDev, AmazonReportsDLQDev
   S3: dzgro-reports-dev, amazon-reports-dev, ...

Environment: STAGING
   Lambda: ApiFunctionStaging
   Lambda: QueueModelMessageProcessorFunctionStaging
   API Gateway: ApiGatewayStaging
   SQS: AmazonReportsQStaging, AmazonReportsDLQStaging
   S3: dzgro-reports-staging, amazon-reports-staging, ...

Environment: PROD
   Lambda: ApiFunctionProd
   Lambda: QueueModelMessageProcessorFunctionProd
   API Gateway: ApiGatewayProd
   SQS: AmazonReportsQProd, AmazonReportsDLQProd
   S3: dzgro-reports-prod, amazon-reports-prod, ...
```

### After (Optimized Deploy)
```
Shared Resources:
   Lambda: ApiFunction (base)
      Alias: dev
      Alias: staging
      Alias: prod
   Lambda: QueueModelMessageProcessorFunction (base)
      Alias: dev
      Alias: staging
      Alias: prod
   HTTP API: /api/{proxy+}
      Stage: dev � Lambda:dev
      Stage: staging � Lambda:staging
      Stage: prod � Lambda:prod
   HTTP API: /webhook/{proxy+}
       Stage: dev � Lambda:dev
       Stage: staging � Lambda:staging
       Stage: prod � Lambda:prod

Environment-Specific Resources:
   DEV:
      SQS: AmazonReportsQDev, AmazonReportsDLQDev
      S3: dzgro-reports-dev, amazon-reports-dev, ...
      Cognito: DzgroUserPoolDev
   STAGING:
      SQS: AmazonReportsQStaging, AmazonReportsDLQStaging
      S3: dzgro-reports-staging, amazon-reports-staging, ...
      Cognito: DzgroUserPoolStaging
   PROD:
      SQS: AmazonReportsQProd, AmazonReportsDLQProd
      S3: dzgro-reports-prod, amazon-reports-prod, ...
      Cognito: DzgroUserPoolProd
   LOCAL:
       SQS: AmazonReportsQLocal, AmazonReportsDLQLocal (no trigger)
       S3: dzgro-reports-local, amazon-reports-local, ...
```

## Resource Count Reduction

| Resource Type | Before (per type) | After (per type) | Savings |
|--------------|-------------------|------------------|---------|
| Lambda Functions | 3-4 | 1 + 3 aliases | ~50-75% |
| API Gateways | 3 (REST) | 1 HTTP API (with 3 stages) | ~67% |
| Certificates | 2 (Auth + API) | 2 (Auth + API) | 0% |
| SQS Queues | 3 | 4 (includes local, excludes Razorpay) | Variable |
| S3 Buckets | 4 | 4 | 0% |
| Cognito Pools | 3 | 3 | 0% |

**Overall**: Significant reduction in Lambda and API Gateway resources, making management much simpler.

## Recent Architecture Changes (Webhook Integration)

### Removed: Separate Webhook HTTP API

**Previous Architecture (Before Recent Changes):**
- **Two separate HTTP APIs**:
  1. API HTTP API: `/api/{proxy+}` with domain-specific CORS
  2. Webhook HTTP API: `/webhook/rzrpay/{proxy+}` with wildcard CORS, direct SQS integration
- **Three certificates**: Auth, API, Webhook
- **Razorpay Webhook Processing**:
  - Webhook HTTP API `/webhook/rzrpay/{proxy+}` → SQS Queue (RazorPayWebhookProcessorQ) → QueueModelMessageProcessor Lambda
  - Headers (X-Razorpay-Signature, x-razorpay-event-id) mapped to SQS message attributes
  - Queue-based asynchronous processing

**Current Architecture (After Recent Changes):**
- **Single HTTP API** with combined routes:
  1. `/api/{proxy+}` → Api Lambda function (with stage variable routing)
  2. `/webhook/rzrpay/{proxy+}` → RazorPayWebhook Lambda function (direct Lambda proxy integration)
- **Two certificates**: Auth, API (single API certificate handles both routes)
- **Razorpay Webhook Processing**:
  - Single HTTP API `/webhook/rzrpay/{proxy+}` → RazorPayWebhook Lambda function (direct)
  - Headers available in Lambda event (payload format 2.0)
  - Direct, synchronous Lambda invocation
- **CORS**: Wildcard (*) on single HTTP API to support both internal API calls and external webhooks

**Benefits of New Architecture:**
1. **Simplified Infrastructure**: One HTTP API instead of two
2. **Reduced Certificate Management**: Two certificates instead of three
3. **Faster Webhook Processing**: Direct Lambda invocation instead of queue-based
4. **Simpler Debugging**: Synchronous processing with immediate responses
5. **Lower Latency**: Eliminates SQS queue delay
6. **Easier Monitoring**: Direct CloudWatch logs from webhook Lambda

**Removed Resources:**
- Webhook HTTP API (WebhookHttpApi)
- Webhook certificate (webhook.{env}.dzgro.com)
- Webhook domain mapping (WebhookHttpApiDomain, WebhookHttpApiMapping)
- Razorpay webhook SQS queue (RazorPayWebhookProcessorQ)
- Razorpay webhook DLQ (RazorPayWebhookProcessorDLQ)
- SQS-based webhook integration configuration

**Added Resources:**
- RazorPayWebhook Lambda function with aliases
- Direct Lambda proxy integration for `/webhook/rzrpay/{proxy+}` route

**Migration Notes:**
- No breaking changes to webhook endpoint URL (`api.{env}.dzgro.com/webhook/rzrpay/...`)
- Razorpay webhook configuration remains unchanged
- Response format remains compatible (HTTP 200 with JSON body)

## Implementation Plan

## Files to Copy vs Files to Create

### 📋 Copy These TRIED & TESTED Files (NO Breaking Changes):

These files are production-tested and optimized. Copy them completely:

1. **SAM Executor** (`deploy/TemplateBuilder/SamExecutor.py`)
   - Destination: `src/sam_deploy/executor/sam_executor.py`
   - Why: Battle-tested deployment logic, WSL integration, stack validation
   - Changes: Only update import paths to work within `sam-deploy/`

2. **Layer Builder** (`deploy/TemplateBuilder/BuildLayers.py`)
   - Destination: `src/sam_deploy/builder/build_layers.py`
   - Why: Highly optimized with caching, parallel builds, metrics
   - Changes: Only update import paths to work within `sam-deploy/`

3. **Docker Manager** (`deploy/TemplateBuilder/docker_manager.py`)
   - Destination: `src/sam_deploy/utils/docker_manager.py`
   - Why: Tested WSL Docker integration for Windows
   - Changes: Only update import paths to work within `sam-deploy/`

### ✨ Create These Files (FULL Customization Freedom):

These files you will create from scratch or heavily customize:

1. **Mapping Configuration** (`src/sam_deploy/config/mapping.py`)
   - Start with: `deploy/TemplateBuilder/StarterMapping.py` as reference
   - Freedom: Complete redesign of models and structure
   - Restriction: Cannot modify imported external library models

2. **Template Builder** (`src/sam_deploy/builder/template_builder.py`)
   - Start with: `deploy/TemplateBuilder/Builder.py` as reference for patterns
   - Freedom: Redesign helper functions, add new ones
   - Changes: Remove environment suffixes, add alias/stage helpers

3. **HTTP API Builders** (`src/sam_deploy/builder/build_http_apis.py`)
   - Create from scratch
   - Reference: `deploy/TemplateBuilder/BuildApiGateway.py` for patterns only
   - New: Single HTTP API with both `/api/{proxy+}` and `/webhook/rzrpay/{proxy+}` routes

4. **Certificate Builder** (`src/sam_deploy/builder/build_certificates.py`)
   - Adapt from: Certificate logic in `deploy/TemplateBuilder/Builder.py`
   - Two certificate types: Auth (us-east-1) and API (region-specific)

5. **Other Builders** (Lambda, Queue, Bucket, Cognito)
   - Adapt from corresponding files in `deploy/TemplateBuilder/`
   - Modify to support alias/stage architecture

### Phase 1: Project Setup
1. Create Poetry project structure in `sam-deploy/`
2. Set up dependencies (boto3, pydantic, python-dotenv, etc.)
3. **Copy (don't reference)** these TRIED & TESTED files from `deploy/`:
   - `SamExecutor.py` → `src/sam_deploy/executor/sam_executor.py`
   - `BuildLayers.py` → `src/sam_deploy/builder/build_layers.py`
   - `docker_manager.py` → `src/sam_deploy/utils/docker_manager.py`
4. **Use as reference** (then create your own):
   - `StarterMapping.py` - Initial structure, then customize freely
   - `Builder.py` - Helper function patterns
   - Other builder files - Implementation patterns

### Phase 2: Core Builder Module
Create `src/sam_deploy/builder/template_builder.py`:
- **Deployment Configuration**: Based on interactive selection at startup
  - Option 1 (Core Product): All resources, all regions
  - Option 2 (AMS Features): AMS resources only, all regions
  - Option 3/4 (Promotions): Lambda alias updates via boto3
- **Region Selection**: All four regions (ap-south-1, eu-west-1, us-east-1, us-west-2)
  - Sequential deployment per region (SAM CLI limitation)
- **Resource Dictionary**: Build SAM template as dict structure per region

#### Helper Functions (from Builder.py)
Adapt these naming helpers for new strategy:

```python
# UNCHANGED - Keep these as-is
getBucketName(name: S3Bucket) -> str
getBucketResourceName(name: S3Bucket) -> str
getQueueName(name: QueueName, type: Literal['Q','DLQ','EventSourceMapping']) -> str
getUserPoolName() -> str
getApiGatewayRoleName() -> str
getDictTag() -> dict
getListTag() -> list[dict]

# MODIFIED - Remove environment suffix or make optional
getFunctionName(name: LambdaName) -> str
    # OLD: f'{name.value}{self.envtextTitle}Function'
    # NEW: f'{name.value}Function'  # No env suffix

getLambdaRoleName(name: LambdaName) -> str
    # OLD: f'{name.value}LambdaRole{self.envtextTitle}'
    # NEW: f'{name.value}LambdaRole'  # No env suffix

# NEW HELPERS
getLambdaAliasName(env: ENVIRONMENT) -> str
    # Returns: 'dev', 'staging', 'prod'

getApiStageName(env: ENVIRONMENT) -> str
    # Returns: 'dev', 'staging', 'prod'
```

### Phase 3: Resource Builders

Create modular builder classes:

#### 3.1 Lambda Builder (`src/sam_deploy/builder/build_lambdas.py`)
- Create base Lambda function (without environment suffix)
- Define Lambda aliases for dev, staging, prod
- Auto-publish configuration for dev
- Set up permissions for each alias
- Configure environment variables per alias using alias configuration

**Key SAM Template Sections**:
```yaml
Resources:
  ApiFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: ApiFunction
      AutoPublishAlias: dev  # Auto-publish to dev
      # ... other properties

  ApiFunctionAliasDev:
    Type: AWS::Lambda::Alias
    Properties:
      FunctionName: !Ref ApiFunction
      FunctionVersion: $LATEST
      Name: dev

  ApiFunctionAliasStaging:
    Type: AWS::Lambda::Alias
    Properties:
      FunctionName: !Ref ApiFunction
      FunctionVersion: !GetAtt ApiFunction.Version
      Name: staging

  ApiFunctionAliasProd:
    Type: AWS::Lambda::Alias
    Properties:
      FunctionName: !Ref ApiFunction
      FunctionVersion: !GetAtt ApiFunction.Version
      Name: prod
```

#### 3.2 HTTP API Builder (`src/sam_deploy/builder/build_http_apis.py`)
Create **single HTTP API** with combined routes and wildcard CORS:

**Combined HTTP API**:
- **Routes**:
  1. `/api/{proxy+}`: Main application API
     - Integration: Lambda proxy to Api function
     - Stage variable routing to correct alias (dev/staging/prod)
     - Methods: ANY (all HTTP methods)
  2. `/webhook/rzrpay/{proxy+}`: Razorpay webhook endpoint
     - Integration: Lambda proxy to RazorPayWebhook function
     - Direct invocation (no queue, no stage variable routing)
     - Method: POST only
     - Headers: X-Razorpay-Signature, x-razorpay-event-id passed in event
- **Custom Domain**: Single API certificate (`api.{env}.dzgro.com`) handles both routes
- **CORS**: Wildcard `*` (allows both internal API calls and external webhooks)
  - AllowOrigins: `*`
  - AllowMethods: GET, POST, PUT, DELETE, PATCH
  - AllowHeaders: Content-Type, Authorization, Marketplace, X-Razorpay-Signature, x-razorpay-event-id
  - MaxAge: 300
- **Stage Variables**: Point to Lambda aliases for API route only (webhook uses direct integration)

**Key SAM Template Sections**:
```yaml
Resources:
  # Combined HTTP API - Wildcard CORS with Lambda Integration for both routes
  ApiHttpApi:
    Type: AWS::Serverless::HttpApi
    Properties:
      StageName: dev
      StageVariables:
        LambdaAlias: dev  # Used for /api route only
      CorsConfiguration:
        AllowOrigins:
          - "*"  # Wildcard to support both API and webhooks
        AllowMethods:
          - GET
          - POST
          - PUT
          - DELETE
          - PATCH
        AllowHeaders:
          - Content-Type
          - Authorization
          - Marketplace
          - X-Razorpay-Signature
          - x-razorpay-event-id
        MaxAge: 300
      DefinitionBody:
        openapi: '3.0.1'
        info:
          title: Dzgro Dev API
          version: '1.0'
        paths:
          # Main API route with stage variable routing
          /api/{proxy+}:
            x-amazon-apigateway-any-method:
              x-amazon-apigateway-integration:
                type: aws_proxy
                httpMethod: POST
                payloadFormatVersion: '2.0'
                uri: !Sub arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${ApiFunction.Arn}:${!stageVariables.LambdaAlias}/invocations

          # Razorpay webhook route with direct Lambda integration
          /webhook/rzrpay/{proxy+}:
            post:
              x-amazon-apigateway-integration:
                type: aws_proxy
                httpMethod: POST
                payloadFormatVersion: '2.0'
                uri: !Sub arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${RazorPayWebhookFunction.Arn}/invocations
```

#### 3.3 Queue Builder (`src/sam_deploy/builder/build_queues.py`)
- Create SQS queues for all 4 environments (including LOCAL)
- Create Dead Letter Queues
- Set up EventSourceMapping for non-LOCAL environments only
- Configure queue policies as needed

**Logic**:
```python
for env in [ENVIRONMENT.DEV, ENVIRONMENT.STAGING, ENVIRONMENT.PROD, ENVIRONMENT.LOCAL]:
    # Create Q and DLQ for all envs
    create_queue(env)
    create_dlq(env)

    # Only create EventSourceMapping for non-LOCAL
    if env != ENVIRONMENT.LOCAL:
        create_event_source_mapping(env)
```

#### 3.4 Bucket Builder (`src/sam_deploy/builder/build_buckets.py`)
- Create S3 buckets for all 4 environments
- Configure lifecycle rules
- Configure CORS rules
- Set up S3 trigger events (where applicable)

#### 3.5 Cognito Builder (`src/sam_deploy/builder/build_cognito.py`)
- Create User Pools for dev, staging, prod (exclude LOCAL)
- Configure User Pool Clients
- Set up Lambda triggers (if applicable)
- Certificate integration for custom domains
- **⚠️ CRITICAL: Create User Pool Domain for Mumbai (ap-south-1) marketplace**
  - Must execute `createUserPoolDomain` via boto3 for each User Pool
  - Required for Cognito Hosted UI and OAuth flows
  - Domain: Uses Auth certificate from us-east-1
  - Execute AFTER User Pool creation but BEFORE deployment completes
  - Reference: See existing implementation for domain creation pattern

#### 3.6 Certificate Builder (`src/sam_deploy/builder/build_certificates.py`)
Create **TWO certificate types** for custom domains using **boto3** (NOT SAM):

**⚠️ CRITICAL: Use boto3 for certificate creation**
- Certificates must be created BEFORE SAM deployment
- HTTP APIs need valid certificate ARNs at deployment time
- Cognito requires certificates in us-east-1 (different region than Lambda)
- Reference: `deploy/TemplateBuilder/Builder.py` deploy function for boto3 logic

**Auth Certificate** (us-east-1):
- Domain: `auth.{env}.dzgro.com` (dev/staging) or `auth.dzgro.com` (prod)
- Region: us-east-1 (required for Cognito)
- Used for Cognito User Pool custom domain

**API Certificate** (region-specific):
- Domain: `api.{env}.dzgro.com` (dev/staging) or `api.dzgro.com` (prod)
- Region: Same as Lambda deployment region
- Used for single HTTP API custom domain (handles both `/api` and `/webhook` routes)
- CORS: Wildcard `*` (supports both API and webhooks)

**Helper Functions**:
```python
def getWildCardCertificateArn(type: Literal['Auth','Api']) -> str:
    """
    Create/retrieve certificate ARN via boto3
    Reference: Builder.py deploy() function
    """
    # Auth: us-east-1 (Cognito requirement)
    # Api: region-specific (handles both API and webhook routes)
    region = 'us-east-1' if type == 'Auth' else self.region
    domain = self.getDomainNameByType(type)

    acm = boto3.client('acm', region_name=region)

    # Check if certificate exists
    # If not, create and validate
    # Return ARN

def getDomainNameByType(type: Literal['Auth','Api']) -> str:
    """
    Generate domain name based on type and environment
    - For prod: {type.lower()}.dzgro.com
    - For dev/staging: {type.lower()}.{env}.dzgro.com
    """
    prefix = type.lower()
    if self.env == ENVIRONMENT.PROD:
        return f"{prefix}.dzgro.com"
    else:
        return f"{prefix}.{self.env.value}.dzgro.com"
```

#### 3.7 Layer Builder (`src/sam_deploy/builder/build_layers.py`)
**⚠️ CRITICAL: This is a TRIED & TESTED file - avoid breaking changes!**

- **Copy complete logic** from `deploy/BuildLayers.py` (do NOT reference it)
- This file is production-tested and highly optimized
- Build Lambda layers for dependencies with caching
- Support parallel layer building (4 workers)
- Advanced features:
  - Multi-stage Docker builds
  - Dependency hashing for cache validation
  - 70-80% faster builds with Docker caching
  - Metrics tracking and performance monitoring
  - Cleanup old layer versions (keeps latest 3)
- Return layer ARNs for Lambda configuration
- **⚠️ IMPORTANT: Check for relative file paths**
  - Review all file read/write operations
  - Update paths to work within `sam-deploy/` directory structure
  - Check layer naming - must be **environment-agnostic** (no env suffix)
    - OLD: `pymongo-deps-dev.zip`, `mangum-deps-staging.zip`
    - NEW: `pymongo-deps.zip`, `mangum-deps.zip`
  - Verify cache directory paths
- **Avoid making breaking changes** unless absolutely necessary
- If changes needed, test thoroughly with all layer types

### Phase 4: SAM Executor Module

Create `src/sam_deploy/executor/sam_executor.py`:
**⚠️ CRITICAL: This is a TRIED & TESTED file - avoid breaking changes!**

- **Copy complete logic** from `deploy/TemplateBuilder/SamExecutor.py` (do NOT reference it)
- This file is production-tested and battle-hardened
- Key features:
  - Template serialization to YAML with NoAliasDumper
  - CloudFormation stack status validation before deployment
  - SAM CLI invocation through WSL (Windows environment)
  - Windows path to WSL path conversion (`/mnt/d/...`)
  - S3 bucket creation for SAM artifacts (per environment)
  - Known SAM CLI bug handling
  - Template cleanup after successful deployment
- **⚠️ IMPORTANT: Check for relative file paths**
  - Review all template save/load operations
  - Update paths to work within `sam-deploy/` directory structure
  - Verify S3 bucket naming for SAM artifacts
  - Check log file paths
  - Ensure template output directory exists
- **Avoid making breaking changes** unless absolutely necessary
- Critical functions to preserve:
  - `check_stack_status()` - Prevents deployment conflicts
  - `run_sam_in_wsl()` - Windows/WSL Docker integration
  - `validate()` - Template validation with bug workarounds
  - `build_deploy_sam_template()` - Main deployment orchestration

### Phase 5: Configuration Mapping

Create `src/sam_deploy/config/mapping.py`:
**✅ FULL CUSTOMIZATION FREEDOM - Design as needed!**

- **Initial structure**: Copy from `deploy/TemplateBuilder/StarterMapping.py` as a starting point
- **Full freedom to customize**: You can completely redesign this file
  - Create NEW Pydantic models with different structures
  - Add/remove/modify properties as needed
  - Change validation rules and default values
  - Reorganize the configuration hierarchy
- **ONLY restriction**: Cannot modify imported external library models
  - ✅ CAN use `ENVIRONMENT` from `dzgroshared.db.enums` (but cannot modify the enum itself)
  - ✅ CAN use `S3Bucket`, `QueueName` from `dzgroshared` models (but cannot modify them)
  - ✅ CAN use `BaseModel` from `pydantic` (but cannot change Pydantic's behavior)
  - ✅ CAN create NEW models that wrap or extend these imported models

**Example Configuration** (fully customizable):
```python
from dzgroshared.db.enums import ENVIRONMENT  # Import from external library
from pydantic import BaseModel  # Import from external library

# NEW custom models - you have FULL FREEDOM here
class HttpApiConfig(BaseModel):
    """Custom model for HTTP API configuration"""
    route: str
    cors_origin: str | list[str]
    methods: list[str]

class LambdaAliasConfig(BaseModel):
    """Custom model for Lambda alias configuration"""
    environments: list[ENVIRONMENT]  # Using imported enum
    auto_publish_env: ENVIRONMENT | None = None

class LambdaProperty(BaseModel):
    """Redesigned Lambda configuration model"""
    name: str
    description: str
    memorySize: int = 128
    timeout: int = 900
    layers: list[str] = []
    http_api: HttpApiConfig | None = None
    webhook_api: HttpApiConfig | None = None
    alias_config: LambdaAliasConfig
    # ... add any properties you need

LAMBDAS = [
    LambdaProperty(
        name="Api",
        description="Main API Lambda function",
        memorySize=1024,
        timeout=30,
        layers=["api", "mangum", "dzgroshared"],
        http_api=HttpApiConfig(
            route='/api/{proxy+}',
            cors_origin='https://dzgro.com',
            methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
        ),
        alias_config=LambdaAliasConfig(
            environments=[ENVIRONMENT.DEV, ENVIRONMENT.STAGING, ENVIRONMENT.PROD],
            auto_publish_env=ENVIRONMENT.DEV
        )
    ),
    # ... other lambdas
]
```

**Design Principles**:
- Keep it simple and maintainable
- Use type hints and Pydantic validation
- Document any non-obvious configuration choices
- Ensure backward compatibility with imported external models

### Phase 6: Main Entry Point

Create `src/sam_deploy/__main__.py`:
- Environment detection from `.env`
- **Interactive region selection** (Core Product vs AMS Features)
- Orchestrate build process
- Handle LOCAL environment bucket creation
- Execute sequential deployment for multi-region AMS

**Deployment Selection Flow**:
```python
def select_deployment_type():
    """Interactive deployment type selection"""
    choices = [
        "Core Product Features (ap-south-1 - Mumbai, India)",
        "AMS Features (Multi-region: EU, NA, FE)",
        "Deploy to Staging 🔒 (Requires OTP)",
        "Deploy to Production 🔒 (Requires OTP)"
    ]
    question = [
        inquirer.List(
            "deployment_type",
            message="Select deployment type:",
            choices=choices
        )
    ]
    answer = inquirer.prompt(question)

    if "Core Product" in answer["deployment_type"]:
        return "core", [Region.DEFAULT]
    elif "AMS Features" in answer["deployment_type"]:
        return "ams", Region.others()
    elif "Staging" in answer["deployment_type"]:
        return "promote_staging", None
    elif "Production" in answer["deployment_type"]:
        return "promote_prod", None

def main():
    builder = TemplateBuilder()

    if builder.env == ENVIRONMENT.LOCAL:
        # Only create S3 buckets and SQS queues locally
        create_local_buckets()
        create_local_queues()
    else:
        deployment_type, regions = select_deployment_type()

        if deployment_type == "core":
            # Core Product Features - ap-south-1
            deploy_core_product_features(regions[0])
        elif deployment_type == "ams":
            # AMS Features - Multi-region sequential deployment
            deploy_ams_features_multiregion(regions)
        elif deployment_type == "promote_staging":
            # Promote DEV → STAGING with OTP verification
            promote_to_staging_with_otp()
        elif deployment_type == "promote_prod":
            # Promote STAGING → PROD with OTP verification
            promote_to_production_with_otp()

def deploy_core_product_features(region: Region):
    """Deploy all core product features to ap-south-1"""
    print(f"Deploying Core Product Features to {region.value}")

    # Build layers ONCE (will be reused if AMS deployment follows)
    layer_arns = build_layers(region)

    # Build all core resources
    build_certificates(region)
    build_cognito(region)
    build_lambda_with_aliases(region, layer_arns)
    build_api_http_api(region)
    build_webhook_http_api(region)
    build_queues_all_envs(region)
    build_buckets(region)

    save_template(region)
    deploy_template(region)

def deploy_ams_features_multiregion(regions: list[Region]):
    """Deploy AMS features to multiple regions sequentially"""
    print(f"Deploying AMS Features to {len(regions)} regions sequentially")

    # Build layers ONCE (shared across all regions)
    print("Building common layers (shared across all AMS regions)...")
    layer_arns_cache = build_layers_once()

    # Deploy to each region sequentially
    for region in regions:
        print(f"\n{'='*80}")
        print(f"Deploying to {region.value}")
        print(f"{'='*80}\n")

        # Get region-specific layer ARNs (publish to this region)
        layer_arns = publish_layers_to_region(region, layer_arns_cache)

        # Build only AMS-specific resources
        build_ams_lambdas(region, layer_arns)  # AmsChange, AmsPerformance
        build_ams_queues(region)  # AMS_CHANGE, AMS_PERFORMANCE queues

        save_template(region)
        deploy_template(region)

        print(f"✅ Successfully deployed to {region.value}\n")

    print(f"\n{'='*80}")
    print(f"✅ All AMS regions deployed successfully!")
    print(f"{'='*80}")

def promote_to_staging_with_otp():
    """Promote Lambda versions from DEV to STAGING with OTP verification"""
    import boto3
    import random

    print("\n🚨 CRITICAL OPERATION: Promote to STAGING")
    print("="*80)

    # Get all Lambda functions
    lambda_client = boto3.client('lambda', region_name=Region.DEFAULT.value)
    all_lambdas = get_all_lambda_functions()  # Returns list of Lambda function names

    # Show current state
    print("\nLambdas to be promoted (DEV → STAGING):")
    version_map = {}
    for lambda_name in all_lambdas:
        try:
            dev_alias = lambda_client.get_alias(
                FunctionName=lambda_name,
                Name='dev'
            )
            version = dev_alias['FunctionVersion']
            version_map[lambda_name] = version
            print(f"  - {lambda_name}: Version {version}")
        except Exception as e:
            print(f"  - {lambda_name}: ⚠️  Could not get DEV version: {e}")

    # Confirmation
    confirm = input("\n⚠️  Proceed with promotion to STAGING? (yes/no): ")
    if confirm.lower() != "yes":
        print("❌ Promotion cancelled")
        return

    # Generate and send OTP
    otp = str(random.randint(100000, 999999))
    send_otp_via_ses(otp, "dzgrotechnologies@gmail.com", "staging")
    print(f"\n📧 OTP sent to dzgrotechnologies@gmail.com")
    print("Please check your email for the OTP code.")

    # Verify OTP (3 attempts)
    for attempt in range(3):
        user_otp = input(f"\nEnter OTP (Attempt {attempt + 1}/3): ")
        if user_otp == otp:
            break
        else:
            if attempt < 2:
                print(f"❌ Invalid OTP. {2 - attempt} attempts remaining.")
            else:
                print("❌ Invalid OTP. Maximum attempts exceeded. Promotion aborted.")
                return

    # Update all Lambda aliases
    print("\n⚡ Updating Lambda aliases to STAGING...")
    success_count = 0
    for lambda_name, version in version_map.items():
        try:
            lambda_client.update_alias(
                FunctionName=lambda_name,
                Name='staging',
                FunctionVersion=version
            )
            print(f"  ✅ {lambda_name}: staging → Version {version}")
            success_count += 1
        except Exception as e:
            print(f"  ❌ {lambda_name}: Failed - {e}")

    print(f"\n{'='*80}")
    print(f"✅ Promoted {success_count}/{len(all_lambdas)} lambdas to STAGING successfully!")
    print(f"{'='*80}")

def promote_to_production_with_otp():
    """Promote Lambda versions from STAGING to PROD with OTP verification"""
    import boto3
    import random

    print("\n🚨🚨 CRITICAL OPERATION: Promote to PRODUCTION 🚨🚨")
    print("="*80)

    # Get all Lambda functions
    lambda_client = boto3.client('lambda', region_name=Region.DEFAULT.value)
    all_lambdas = get_all_lambda_functions()

    # Show current state
    print("\nLambdas to be promoted (STAGING → PRODUCTION):")
    version_map = {}
    for lambda_name in all_lambdas:
        try:
            staging_alias = lambda_client.get_alias(
                FunctionName=lambda_name,
                Name='staging'
            )
            version = staging_alias['FunctionVersion']
            version_map[lambda_name] = version
            print(f"  - {lambda_name}: Version {version}")
        except Exception as e:
            print(f"  - {lambda_name}: ⚠️  Could not get STAGING version: {e}")

    # Confirmation
    confirm = input("\n⚠️⚠️  Proceed with promotion to PRODUCTION? (yes/no): ")
    if confirm.lower() != "yes":
        print("❌ Promotion cancelled")
        return

    # Generate and send OTP
    otp = str(random.randint(100000, 999999))
    send_otp_via_ses(otp, "dzgrotechnologies@gmail.com", "production")
    print(f"\n📧 OTP sent to dzgrotechnologies@gmail.com")
    print("Please check your email for the OTP code.")

    # Verify OTP (3 attempts)
    for attempt in range(3):
        user_otp = input(f"\nEnter OTP (Attempt {attempt + 1}/3): ")
        if user_otp == otp:
            break
        else:
            if attempt < 2:
                print(f"❌ Invalid OTP. {2 - attempt} attempts remaining.")
            else:
                print("❌ Invalid OTP. Maximum attempts exceeded. Promotion aborted.")
                return

    # Update all Lambda aliases
    print("\n⚡ Updating Lambda aliases to PRODUCTION...")
    success_count = 0
    for lambda_name, version in version_map.items():
        try:
            lambda_client.update_alias(
                FunctionName=lambda_name,
                Name='prod',
                FunctionVersion=version
            )
            print(f"  ✅ {lambda_name}: prod → Version {version}")
            success_count += 1
        except Exception as e:
            print(f"  ❌ {lambda_name}: Failed - {e}")

    print(f"\n{'='*80}")
    print(f"✅ Promoted {success_count}/{len(all_lambdas)} lambdas to PRODUCTION successfully!")
    print(f"{'='*80}")

def send_otp_via_ses(otp: str, recipient: str, stage: str):
    """Send OTP via AWS SES with stage information"""
    import boto3

    ses = boto3.client('ses', region_name='ap-south-1')

    subject = f"🔒 SAM Deploy: Lambda Promotion OTP - {stage.upper()}"
    body = f"""
Lambda Alias Promotion OTP

Target Stage: {stage.upper()}

Your One-Time Password (OTP) for Lambda alias promotion:

{otp}

This OTP is valid for this session only.
Do not share this code with anyone.

If you did not initiate this deployment, please contact your administrator immediately.

---
Dzgro Technologies
Generated by SAM Deploy System
"""

    try:
        ses.send_email(
            Source='noreply@dzgro.com',  # Must be verified in SES
            Destination={'ToAddresses': [recipient]},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Text': {'Data': body}}
            }
        )
        print(f"📧 Email sent successfully to {recipient} for {stage.upper()} promotion")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        raise
```

### Phase 7: Configuration Management

Create `.env` file structure:
```env
# AWS Configuration
AWS_ACCOUNT_ID=123456789012
AWS_PROFILE=default  # Optional

# Note: Environment (dev/staging/prod) is determined by deployment option selected
# Note: Regions are hardcoded (all four regions deployed sequentially)
```

**Region Configuration in Code:**
```python
# In src/sam_deploy/config/mapping.py

class Region(str, Enum):
    # Core Product Region
    DEFAULT = 'ap-south-1'  # Mumbai, India - Core Product Features

    # AMS-only Regions
    EU = "eu-west-1"   # Europe (Ireland) - AMS Features only
    NA = "us-east-1"   # North America (N. Virginia) - AMS Features only
    FE = "us-west-2"   # Far East (Oregon) - AMS Features only

    @staticmethod
    def core_product():
        """Returns core product region"""
        return [Region.DEFAULT]

    @staticmethod
    def ams_regions():
        """Returns AMS-only regions"""
        return [Region.EU, Region.NA, Region.FE]
```

### Phase 8: Error Handling & Progress Tracking

**⚠️ CRITICAL: Implement comprehensive error handling and user feedback**

All deployment operations must include:

1. **Progress Tracking**:
   - Show percentage completion where possible
   - Example: `[3/10] Building Lambda layers... 30% complete`
   - For multi-step operations: `Step 2 of 5: Creating certificates...`
   - For multi-region: `Region 2/4 (eu-west-1): Deploying resources...`

2. **Status Updates**:
   ```python
   # Example implementation
   def deploy_with_progress(regions: list[Region]):
       total_steps = len(regions) * 8  # 8 major steps per region
       current_step = 0

       for idx, region in enumerate(regions, 1):
           print(f"\n{'='*80}")
           print(f"Region {idx}/{len(regions)}: {region.value}")
           print(f"{'='*80}\n")

           # Step 1: Certificates
           current_step += 1
           print(f"[{current_step}/{total_steps}] 🔒 Creating certificates...")
           try:
               create_certificates(region)
               print(f"  ✅ Certificates created successfully")
           except Exception as e:
               print(f"  ❌ Failed to create certificates: {e}")
               raise

           # Step 2: Cognito
           current_step += 1
           print(f"[{current_step}/{total_steps}] 👤 Creating Cognito User Pools...")
           try:
               create_cognito(region)
               print(f"  ✅ Cognito User Pools created")
           except Exception as e:
               print(f"  ❌ Failed to create Cognito: {e}")
               raise

           # ... continue for all steps

       completion_pct = (current_step / total_steps) * 100
       print(f"\n📊 Overall Progress: {completion_pct:.1f}% complete")
   ```

3. **Layer Building Progress**:
   ```python
   # For layer building (parallel operations)
   def build_layers_with_progress(layer_configs: list):
       total_layers = len(layer_configs)
       completed = 0

       print(f"📦 Building {total_layers} Lambda layers...")

       for layer in layer_configs:
           completed += 1
           pct = (completed / total_layers) * 100
           print(f"  [{completed}/{total_layers}] {layer.name}... {pct:.0f}%")

           try:
               build_layer(layer)
               print(f"    ✅ {layer.name} built successfully")
           except Exception as e:
               print(f"    ❌ Failed to build {layer.name}: {e}")
               raise
   ```

4. **Error Handling**:
   - Use try/except blocks for ALL AWS API calls
   - Provide clear error messages with context
   - Include retry logic for transient failures (exponential backoff)
   - Log errors to file for debugging

   ```python
   import time
   from typing import Callable, Any

   def retry_with_backoff(func: Callable, max_retries: int = 3) -> Any:
       """Retry function with exponential backoff"""
       for attempt in range(max_retries):
           try:
               return func()
           except Exception as e:
               if attempt < max_retries - 1:
                   wait_time = 2 ** attempt  # 1s, 2s, 4s
                   print(f"  ⚠️  Attempt {attempt + 1} failed: {e}")
                   print(f"  ⏳ Retrying in {wait_time}s...")
                   time.sleep(wait_time)
               else:
                   print(f"  ❌ All {max_retries} attempts failed")
                   raise
   ```

5. **Certificate Creation Feedback**:
   ```python
   def create_certificate_with_progress(domain: str, region: str):
       print(f"  🔍 Checking existing certificate for {domain}...")

       existing_cert = check_existing_certificate(domain, region)
       if existing_cert:
           print(f"  ✅ Using existing certificate: {existing_cert['Arn']}")
           return existing_cert['Arn']

       print(f"  📝 Creating new certificate for {domain}...")
       cert_arn = create_certificate(domain, region)
       print(f"  ⏳ Waiting for certificate validation...")

       # Show validation progress
       while not is_certificate_validated(cert_arn, region):
           print(f"    ⏳ Still waiting... (DNS validation required)")
           time.sleep(10)

       print(f"  ✅ Certificate validated: {cert_arn}")
       return cert_arn
   ```

6. **SAM Deployment Progress**:
   - Capture SAM CLI output and parse for progress
   - Show CloudFormation stack events in real-time
   - Indicate when deployment is waiting for resources

   ```python
   def deploy_sam_with_progress(template_file: str, stack_name: str):
       print(f"🚀 Deploying CloudFormation stack: {stack_name}")
       print(f"  📄 Template: {template_file}")

       # Run SAM deploy
       process = run_sam_deploy_async(template_file, stack_name)

       # Monitor stack events
       cf = boto3.client('cloudformation')
       last_event_time = datetime.now()

       while process.poll() is None:
           events = cf.describe_stack_events(StackName=stack_name)
           new_events = [e for e in events['StackEvents']
                        if e['Timestamp'] > last_event_time]

           for event in reversed(new_events):
               status = event['ResourceStatus']
               resource = event['LogicalResourceId']
               print(f"    {status}: {resource}")
               last_event_time = event['Timestamp']

           time.sleep(5)

       print(f"  ✅ Stack deployment completed")
   ```

7. **Cognito User Pool Domain Creation**:
   ```python
   def create_user_pool_domain_with_progress(pool_id: str, domain: str, cert_arn: str):
       print(f"  🌐 Creating User Pool domain: {domain}")

       try:
           cognito = boto3.client('cognito-idp', region_name='ap-south-1')
           cognito.create_user_pool_domain(
               Domain=domain,
               UserPoolId=pool_id,
               CustomDomainConfig={'CertificateArn': cert_arn}
           )
           print(f"  ⏳ Waiting for domain to become active...")

           # Wait for domain to be active
           while True:
               response = cognito.describe_user_pool_domain(Domain=domain)
               status = response['DomainDescription']['Status']

               if status == 'ACTIVE':
                   print(f"  ✅ User Pool domain active")
                   break
               elif status == 'FAILED':
                   print(f"  ❌ User Pool domain creation failed")
                   raise Exception(f"Domain creation failed")
               else:
                   print(f"    Status: {status}... waiting")
                   time.sleep(10)
       except Exception as e:
           print(f"  ❌ Failed to create User Pool domain: {e}")
           raise
   ```

8. **S3 and Queue Creation (Local)**:
   ```python
   def create_local_resources_with_progress():
       print("📦 Creating LOCAL environment resources...")

       # S3 Buckets
       buckets = get_bucket_list()
       print(f"\n  Creating {len(buckets)} S3 buckets...")
       for idx, bucket in enumerate(buckets, 1):
           print(f"  [{idx}/{len(buckets)}] {bucket.name}")
           try:
               create_s3_bucket(bucket)
               print(f"    ✅ Created")
           except Exception as e:
               print(f"    ❌ Failed: {e}")
               raise

       # SQS Queues
       queues = get_queue_list()
       print(f"\n  Creating {len(queues)} SQS queues...")
       for idx, queue in enumerate(queues, 1):
           print(f"  [{idx}/{len(queues)}] {queue.name}")
           try:
               create_sqs_queue(queue)
               print(f"    ✅ Created")
           except Exception as e:
               print(f"    ❌ Failed: {e}")
               raise

       print(f"\n✅ All LOCAL resources created successfully")
   ```

### Phase 9: Testing Strategy

1. **Unit Tests**: Test helper functions for naming conventions
2. **Integration Tests**: Test template generation for each environment
3. **Deployment Tests**: Test actual deployment to dev environment
4. **Validation Tests**: Verify alias and stage variable configuration
5. **Error Handling Tests**: Test retry logic and error recovery
6. **Progress Tracking Tests**: Verify all progress indicators work correctly

## Critical Naming Conventions

### Do NOT Change (unless critical):
- `getBucketName()` - S3 bucket naming
- `getQueueName()` - SQS queue naming
- `getUserPoolName()` - Cognito User Pool naming
- `getDomainNameByType()` - Domain name generation

### MUST Change:
- `getFunctionName()` - Remove environment suffix
- `getLambdaRoleName()` - Consider making environment-agnostic
- `getApiGatewayName()` - Remove environment suffix
- `getWildCardCertificateArn()` - Support 'Auth' and 'Api' types only
- `getDomainNameByType()` - Support 'Auth' and 'Api' types only

### NEW Helpers Needed:
- `getLambdaAliasName(env)` - Generate alias names
- `getApiStageName(env)` - Generate stage names
- `getLambdaArnWithAlias(function, alias)` - Helper for ARN construction
- `getApiHttpApiName()` - Name for single HTTP API (handles both /api and /webhook routes)

## Migration Considerations

### Breaking Changes from Old Deploy Project
1. Lambda function names no longer include environment suffix
2. API Gateway moves from REST API to single HTTP API (with combined routes)
3. Stage variables replace separate API Gateways
4. Event source mappings now reference Lambda aliases
5. Webhook processing: direct Lambda invocation instead of SQS queue
6. Two certificates instead of previous configurations (Auth, API)

### Backward Compatibility
- Existing bucket names remain unchanged
- Queue names remain unchanged
- Cognito pools remain unchanged
- Can deploy alongside old infrastructure initially
- Separate CloudFormation stack (no conflicts)

### Migration & Deletion Strategy

**Phase 1: Parallel Deployment**
1. Deploy `sam-deploy` to separate CloudFormation stack
2. Test thoroughly in dev environment
3. Validate all integrations (API, webhooks, queues, etc.)

**Phase 2: Traffic Migration**
1. Use weighted alias routing for gradual traffic shift
2. Monitor metrics and error rates
3. Rollback capability via alias versions

**Phase 3: Old Infrastructure Decommission**
1. Once fully migrated, delete old CloudFormation stack
2. **DELETE the `deploy/` project directory**
3. Update documentation to reference only `sam-deploy/`

> ⚠️ **IMPORTANT**: After migration, the `deploy/` project will be DELETED. The `sam-deploy/` project must be completely self-contained with NO dependencies on `deploy/`.

## Advantages of New Approach

1. **Simplified Management**:
   - Single Lambda function to update
   - Single codebase for all environments
   - Easier version control

2. **Cost Optimization**:
   - Fewer Lambda functions to maintain
   - Reduced API Gateway count
   - Shared resources reduce overhead

3. **Deployment Flexibility**:
   - Can use alias traffic shifting for blue/green deployments
   - Version-based rollback capability
   - Environment-specific configurations via alias environment variables

4. **Better Resource Utilization**:
   - Lambda code deployed once, aliased multiple times
   - HTTP API is more cost-effective than REST API
   - Stage variables provide runtime flexibility

## Reference Structure

```
sam-deploy/
   pyproject.toml
   README.md
   .env.example
   src/
      sam_deploy/
          __init__.py
          __main__.py
          builder/
             __init__.py
             template_builder.py
             build_lambdas.py
             build_api.py
             build_queues.py
             build_buckets.py
             build_cognito.py
             build_layers.py
          executor/
             __init__.py
             sam_executor.py
          config/
             __init__.py
             mapping.py
          utils/
              __init__.py
              helpers.py
   tests/
       __init__.py
       test_builder.py
       test_naming.py
       test_template.py
```

## Next Steps

1. Set up Poetry dependencies in `pyproject.toml`
2. Create base `TemplateBuilder` class with adapted helper functions
3. Implement certificate builder for Auth, API, and Webhook domains
4. Implement Lambda builder with alias support
5. Implement HTTP API builders (API + Webhook) with different CORS configurations
6. Adapt queue builder to include LOCAL environment
7. Test in dev environment
8. Validate alias and stage variable routing
9. Verify CORS configurations for both HTTP APIs
10. Document migration process from old to new infrastructure

## Dependencies

```toml
[project.dependencies]
boto3 = "^1.28.0"
pydantic = "^2.0.0"
python-dotenv = "^1.0.0"
PyYAML = "^6.0"
inquirer = "^3.1.0"
```

## Usage

```bash
# Set environment
export ENV=dev  # or staging, prod, local

# Run deployment (interactive region selection)
poetry run python -m sam_deploy
```

**Interactive Prompts:**
```
? Select deployment type: (Use arrow keys)
 ❯ Core Product Features (ap-south-1 - Mumbai, India)
   AMS Features (Multi-region: EU, NA, FE)
   Deploy to Staging 🔒 (Requires OTP)
   Deploy to Production 🔒 (Requires OTP)
```

**Example Deployment Flow:**

**Option 1: Core Product Features**
```
$ poetry run python -m sam_deploy
? Select deployment type: Core Product Features (ap-south-1 - Mumbai, India)

🌏 Deploying Core Product Features to ap-south-1
================================================================================
📦 Building common layers (will be cached)...
   - pymongo-deps.zip (cached)
   - mangum-deps.zip (built)
   - dzgroshared.zip (cached)
   ...
🔒 Creating certificates (Auth, API)...
👤 Creating Cognito User Pool...
⚡ Creating Lambda functions with aliases...
🌐 Creating single HTTP API with combined routes...
📬 Creating SQS queues for all environments...
🗄️  Creating S3 buckets...
✅ Successfully deployed to ap-south-1
```

**Option 2: AMS Features**
```
$ poetry run python -m sam_deploy
? Select deployment type: AMS Features (Multi-region: EU, NA, FE)

🔌 Deploying AMS Features to 4 regions sequentially
================================================================================
📦 Building common layers (shared across all regions)...
   - pymongo-deps.zip (built)
   ...

================================================================================
Deploying to eu-west-1
================================================================================
⚡ Creating AMS Lambdas (AmsChange, AmsPerformance)...
📬 Creating AMS queues...
✅ Successfully deployed to eu-west-1

================================================================================
Deploying to us-east-1
================================================================================
⚡ Creating AMS Lambdas (AmsChange, AmsPerformance)...
📬 Creating AMS queues...
✅ Successfully deployed to us-east-1

================================================================================
Deploying to us-west-2
================================================================================
⚡ Creating AMS Lambdas (AmsChange, AmsPerformance)...
📬 Creating AMS queues...
✅ Successfully deployed to us-west-2

================================================================================
✅ All AMS regions deployed successfully!
================================================================================
```

**Option 3: Deploy to Staging**
```
$ poetry run python -m sam_deploy
? Select deployment type: Deploy to Staging 🔒 (Requires OTP)

🚨 CRITICAL OPERATION: Promote to STAGING
================================================================================

Lambdas to be promoted (DEV → STAGING):
  - ApiFunction: Version 47
  - QueueModelMessageProcessorFunction: Version 23
  - CognitoTriggerFunction: Version 12
  - DzgroReportsS3TriggerFunction: Version 8

⚠️  Proceed with promotion to STAGING? (yes/no): yes

📧 OTP sent to dzgrotechnologies@gmail.com
Please check your email for the OTP code.

Enter OTP (Attempt 1/3): 847392

⚡ Updating Lambda aliases to STAGING...
  ✅ ApiFunction: staging → Version 47
  ✅ QueueModelMessageProcessorFunction: staging → Version 23
  ✅ CognitoTriggerFunction: staging → Version 12
  ✅ DzgroReportsS3TriggerFunction: staging → Version 8

================================================================================
✅ Promoted 4/4 lambdas to STAGING successfully!
================================================================================
```

**Option 4: Deploy to Production**
```
$ poetry run python -m sam_deploy
? Select deployment type: Deploy to Production 🔒 (Requires OTP)

🚨🚨 CRITICAL OPERATION: Promote to PRODUCTION 🚨🚨
================================================================================

Lambdas to be promoted (STAGING → PRODUCTION):
  - ApiFunction: Version 47
  - QueueModelMessageProcessorFunction: staging → Version 23
  - CognitoTriggerFunction: Version 12
  - DzgroReportsS3TriggerFunction: Version 8

⚠️⚠️  Proceed with promotion to PRODUCTION? (yes/no): yes

📧 OTP sent to dzgrotechnologies@gmail.com
Please check your email for the OTP code.

Enter OTP (Attempt 1/3): 923741

⚡ Updating Lambda aliases to PRODUCTION...
  ✅ ApiFunction: prod → Version 47
  ✅ QueueModelMessageProcessorFunction: prod → Version 23
  ✅ CognitoTriggerFunction: prod → Version 12
  ✅ DzgroReportsS3TriggerFunction: prod → Version 8

================================================================================
✅ Promoted 4/4 lambdas to PRODUCTION successfully!
================================================================================
```

## Important Notes

1. **Regional Deployment Types**:
   - **Core Product Features** (ap-south-1): All resources deployed
   - **AMS Features** (eu-west-1, us-east-1, us-west-2): Only AMS Lambdas and queues
   - Interactive selection during deployment
   - Layers built once and shared across all regions

2. **Sequential Multi-Region Deployment**:
   - SAM CLI supports only **ONE region at a time**
   - AMS Features deployment is **SEQUENTIAL** (not parallel)
   - Typical deployment time: 5-10 minutes per region
   - Total for all 3 AMS regions: 15-30 minutes
   - Layer building is done ONCE (saves significant time)

3. **Local Environment**:
   - Creates S3 buckets and SQS queues only
   - Queues are NOT triggered by Lambda (no EventSourceMapping)
   - No Lambda, API Gateway, or Cognito resources
   - Region selection is skipped for LOCAL

4. **Lambda Alias Promotion**:
   - **DEV**: Auto-publishes on each deployment (Options 1 & 2)
   - **STAGING**: Manually promoted from DEV via Option 3 (OTP required)
   - **PROD**: Manually promoted from STAGING via Option 4 (OTP required)
   - Promotion is **instant** (updates alias pointer, no redeploy)
   - **Security**: OTP verification via SES email (`dzgrotechnologies@gmail.com`)
   - **3 OTP attempts** allowed per promotion

5. **HTTP API Stages** (Core Product only):
   - Each stage uses stage variables to route to correct alias (for `/api` route)
   - Single custom domain per stage: `api.{stage}.dzgro.com` (handles both `/api` and `/webhook` routes)
   - CORS configured with wildcard `*` to support both internal API calls and external webhooks
   - AllowHeaders include: Content-Type, Authorization, Marketplace, X-Razorpay-Signature, x-razorpay-event-id

6. **Layer Optimization**:
   - Layers built during first deployment
   - Cached locally with dependency hash validation
   - Reused across all regions (published with region-specific ARN)
   - 70-80% time savings for multi-region deployments

7. **OTP Verification Security**:
   - Required for STAGING and PRODUCTION promotions
   - 6-digit random OTP sent via AWS SES
   - Email: `dzgrotechnologies@gmail.com`
   - **SES Configuration Required**:
     - Email `noreply@dzgro.com` must be verified in SES
     - SES must be in production mode (not sandbox)
     - Region: ap-south-1
   - 3 attempts allowed per session
   - OTP valid for current session only

8. **Resource Tagging**:
   - All resources tagged with Project and Environment
   - Enables cost tracking and resource management per region

## Reference Documentation

**External Documentation:**
- SAM documentation: https://docs.aws.amazon.com/serverless-application-model/
- Lambda Aliases: https://docs.aws.amazon.com/lambda/latest/dg/configuration-aliases.html
- HTTP API: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api.html
- CloudFormation: https://docs.aws.amazon.com/cloudformation/
- Pydantic: https://docs.pydantic.dev/

**Initial Reference Files (for setup only, will be copied):**
> ⚠️ These files are used ONLY as reference during initial setup. After copying the tried & tested files (SAM executor, layer builder, docker manager), you will NOT reference the `deploy/` project anymore.

- `deploy/TemplateBuilder/SamExecutor.py` - Copy to `sam_deploy/executor/`
- `deploy/TemplateBuilder/BuildLayers.py` - Copy to `sam_deploy/builder/`
- `deploy/TemplateBuilder/docker_manager.py` - Copy to `sam_deploy/utils/`
- `deploy/TemplateBuilder/StarterMapping.py` - Use as starting point, then customize
- `deploy/TemplateBuilder/Builder.py` - Reference for helper function patterns

**After Setup:**
- The `deploy/` project will be **DELETED** after migration
- All code must be self-contained in `sam-deploy/`
- No runtime dependencies on `deploy/` project
