# SAM Deployment Guide

This document tracks the AWS SAM serverless deployment for the WoS Bear's Den application.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CloudFront                                   │
│                    (Frontend CDN Distribution)                       │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                 ┌──────────────────┴──────────────────┐
                 ▼                                      ▼
┌─────────────────────────┐              ┌─────────────────────────────┐
│     S3 Bucket           │              │     API Gateway (HTTP)      │
│  (Static Frontend)      │              │   api.wos.randomchaoslabs   │
│  - Next.js static export│              └─────────────────────────────┘
└─────────────────────────┘                            │
                                    ┌──────────────────┼──────────────────┐
                                    ▼                  ▼                  ▼
                           ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
                           │   Lambda     │  │   Lambda     │  │   Lambda     │
                           │   Auth       │  │   Heroes     │  │   Admin      │
                           └──────────────┘  └──────────────┘  └──────────────┘
                                    │                  │                  │
                                    └──────────────────┼──────────────────┘
                                                       ▼
                           ┌─────────────────────────────────────────────────┐
                           │              DynamoDB Tables                     │
                           │  MainTable | AdminTable | ReferenceTable        │
                           └─────────────────────────────────────────────────┘
                                                       │
                           ┌─────────────────────────────────────────────────┐
                           │              Cognito User Pool                   │
                           │         (Authentication & Authorization)         │
                           └─────────────────────────────────────────────────┘
```

## Environments

| Environment | Stack Name | Domain | Status |
|-------------|------------|--------|--------|
| **Dev** | wos-dev | wosdev.randomchaoslabs.com | Deploying |
| **Live** | wos-live | wos.randomchaoslabs.com | Not deployed |

## AWS Resources Created

### Lambda Functions (10 total)

| Function | Handler | Purpose |
|----------|---------|---------|
| UserMigrationFunction | auth.migrate_user | Cognito user migration trigger |
| AuthFunction | auth.handler | Login, register, token refresh |
| HeroesFunction | heroes.handler | Hero CRUD, user hero management |
| ProfilesFunction | profiles.handler | User profile management |
| ChiefFunction | chief.handler | Chief gear, charms |
| RecommendFunction | recommendations.handler | Upgrade recommendations |
| AdvisorFunction | advisor.handler | AI advisor chat |
| AdminFunction | admin.handler | Admin dashboard APIs |
| GeneralFunction | general.handler | Events, lineups, misc |
| ScheduledCleanupFunction | general.cleanup | Daily cleanup (CloudWatch scheduled) |

### DynamoDB Tables (3 total)

| Table | Purpose | Key Schema |
|-------|---------|------------|
| MainTable | User data, heroes, profiles | PK: USER#id, SK: varies |
| AdminTable | Admin settings, feature flags, feedback | PK: ADMIN#type, SK: varies |
| ReferenceTable | Static game data (heroes, events) | PK: REF#type, SK: varies |

### Other Resources

- **Cognito User Pool** - Authentication with custom attributes
- **Cognito App Client** - Frontend auth client (no secret)
- **S3 Bucket** - Static frontend hosting
- **CloudFront Distribution** - CDN for frontend
- **Secrets Manager** - API keys (Anthropic, OpenAI)
- **Custom Domains** - API Gateway and CloudFront

## Deployment Commands

### Prerequisites

```bash
# Install AWS SAM CLI
pip install aws-sam-cli

# Configure AWS credentials
aws configure
# Or use environment variables:
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
export AWS_DEFAULT_REGION=us-east-1
```

### Build

```bash
cd infra

# Build all functions (uses cache for speed)
sam build

# Build without cache (clean build)
sam build --no-cached
```

### Deploy to Dev

```bash
cd infra

# First deployment (guided)
sam deploy --guided

# Subsequent deployments
sam deploy

# Or with explicit config
sam deploy --config-env default
```

### Deploy to Live

```bash
cd infra

# Use live config
sam deploy --config-env live

# With confirmation (recommended for prod)
sam deploy --config-env live --confirm-changeset
```

### Validate Template

```bash
cd infra
sam validate
sam validate --lint  # More thorough validation
```

### View Logs

```bash
# Tail logs for a function
sam logs -n AuthFunction --stack-name wos-dev --tail

# Get recent logs
sam logs -n AdvisorFunction --stack-name wos-dev --start-time '5min ago'
```

### Delete Stack

```bash
# Delete dev stack
sam delete --stack-name wos-dev

# Delete live stack (be careful!)
sam delete --stack-name wos-live
```

## Configuration Files

### samconfig.toml

```toml
# infra/samconfig.toml
[default.deploy.parameters]
stack_name = "wos-dev"
resolve_s3 = true
s3_prefix = "wos-dev"
region = "us-east-1"
confirm_changeset = true
capabilities = "CAPABILITY_IAM CAPABILITY_AUTO_EXPAND"
parameter_overrides = "Stage=dev"

[live.deploy.parameters]
stack_name = "wos-live"
# ... similar but Stage=live
```

### Template Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Stage | dev | Environment (dev/live) |
| DomainName | randomchaoslabs.com | Base domain |
| ApiDomainPrefix | api | API subdomain prefix |
| FrontendDomainPrefix | wos | Frontend subdomain prefix |
| CertificateArn | "" | ACM certificate for custom domains |

## Deployment History

### 2026-02-03 - Initial Dev Deployment (SUCCESS)

**Branch:** feature/aws-serverless

**Issues Fixed:**
1. **Circular dependency** - Removed UserMigration from Cognito LambdaConfig
   - Issue: UserPool → UserMigrationFunction → HttpApi (via Globals env) → UserPool
   - Solution: Add UserMigration trigger via separate update after initial deploy

2. **Lambda policy size limit** - AdminFunction had 65 routes = 20KB+ policy
   - Issue: "The final policy size (20681) is bigger than the limit (20480)"
   - Solution: Replaced 65 individual routes with 4 catch-all routes using `{proxy+}`
   - Handler uses `APIGatewayHttpResolver` for internal routing

**Commands Run:**
```bash
cd infra
sam build
sam deploy --no-confirm-changeset
```

**Status:** ✅ SUCCESS

**Stack Outputs (Dev):**
| Resource | Value |
|----------|-------|
| API URL | https://qro6iih6oe.execute-api.us-east-1.amazonaws.com/dev |
| CloudFront URL | https://d3q6j2q80oj6gu.cloudfront.net |
| User Pool ID | us-east-1_KvZMywYFF |
| User Pool Client ID | 52393513i04q1pe1rk61eqq5oh |
| Frontend S3 Bucket | wos-frontend-dev-561893854848 |
| CloudFront Distribution ID | E1CU7UPD2I54BY |
| Main Table | wos-main-dev |
| Admin Table | wos-admin-dev |
| Reference Table | wos-reference-dev |

**Next Steps:**
1. Configure API keys in Secrets Manager
2. Deploy frontend to S3 bucket
3. (Optional) Add UserMigration trigger to Cognito
4. (Optional) Configure custom domains

---

## Known Issues & Workarounds

### Circular Dependency - UserMigration

The Cognito UserPool can't reference the UserMigration Lambda at creation time due to circular dependencies.

**Workaround:**
1. Deploy without UserMigration trigger
2. After deployment, manually add trigger via AWS Console or CLI:
   ```bash
   aws cognito-idp update-user-pool \
     --user-pool-id <pool-id> \
     --lambda-config UserMigration=<lambda-arn>
   ```

### Custom Domains

Custom domains require:
1. ACM certificate in us-east-1 (for CloudFront)
2. Route53 hosted zone or manual DNS configuration
3. Certificate ARN passed as parameter

## Rollback Procedure

```bash
# View deployment history
aws cloudformation describe-stack-events --stack-name wos-dev

# Rollback to previous version
aws cloudformation rollback-stack --stack-name wos-dev

# Or delete and redeploy
sam delete --stack-name wos-dev
sam deploy
```

## Monitoring

### CloudWatch Dashboards

After deployment, access logs and metrics at:
- https://console.aws.amazon.com/cloudwatch/home?region=us-east-1

### Key Metrics to Monitor

- Lambda invocations and errors
- API Gateway 4xx/5xx errors
- DynamoDB consumed capacity
- Cognito sign-in attempts

## Cost Estimates (Dev Environment)

| Service | Estimate/Month | Notes |
|---------|---------------|-------|
| Lambda | ~$0 | Free tier covers low usage |
| API Gateway | ~$0 | Free tier: 1M requests |
| DynamoDB | ~$0 | On-demand, free tier |
| S3 | ~$1 | Static hosting |
| CloudFront | ~$0 | Free tier: 1TB |
| Cognito | ~$0 | Free tier: 50K MAU |
| Secrets Manager | ~$0.40 | 1 secret @ $0.40/month |
| **Total** | **~$1-2/month** | Mostly free tier eligible |

### Cost Optimizations Applied

- **DynamoDB**: PAY_PER_REQUEST (on-demand) - no idle cost
- **CloudFront**: PriceClass_100 (cheapest - US/Canada/Europe only)
- **Lambda**: No provisioned concurrency - only pay for invocations
- **Scheduled Jobs**: Once per day (not hourly)
- **Lambda Memory**: Minimal sizes (128-512MB based on need)

## Frontend Deployment

The frontend is a Next.js app exported as static files.

```bash
cd frontend

# Build static export
npm run build

# Sync to S3 (after SAM deployment)
aws s3 sync out/ s3://wos-dev-frontend-bucket --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id <dist-id> \
  --paths "/*"
```

## Secrets Management

API keys are stored in AWS Secrets Manager:

```bash
# Create/update secrets (done once)
aws secretsmanager create-secret \
  --name wos-dev/api-keys \
  --secret-string '{"ANTHROPIC_API_KEY":"sk-...", "OPENAI_API_KEY":"sk-..."}'

# Update existing secret
aws secretsmanager update-secret \
  --secret-id wos-dev/api-keys \
  --secret-string '{"ANTHROPIC_API_KEY":"sk-...", "OPENAI_API_KEY":"sk-..."}'
```

Lambda functions access secrets via the SECRETS_ARN environment variable.
