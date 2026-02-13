# Deployment Guide

## AWS CLI

**Path:** `"C:\Program Files\Amazon\AWSCLIV2\aws.exe"`

## Architecture Overview

Fully serverless stack deployed via SAM/CloudFormation:

| Layer | Service | Details |
|-------|---------|---------|
| Frontend | S3 + CloudFront | Next.js static export |
| API | API Gateway (HTTP) | Routes to Lambda functions |
| Backend | Lambda (Python 3.13) | 10 functions (Auth, Heroes, Profiles, Chief, Recommend, Advisor, Admin, General, Cleanup, UserMigration) |
| Database | DynamoDB | 3 tables per environment (main, admin, reference) |
| Auth | Cognito | Email-based user pool |
| Secrets | Secrets Manager | API keys and sensitive config |
| Email | SES | Transactional emails (sandbox mode) |

## Environments

| Name | Stack | URL | Database | Cost |
|------|-------|-----|----------|------|
| **Local** | Your machine (localhost:3000) | N/A | N/A | Free |
| **Dev** | SAM `wos-dev` | wosdev.randomchaoslabs.com | DynamoDB (dev tables) | ~$0 at low traffic |
| **Live** | SAM `wos-live` | wos.randomchaoslabs.com | DynamoDB (live tables) | ~$0 at low traffic |
| **Landing** | Lightsail `randomchaoslabs-server` | www.randomchaoslabs.com | N/A | $5/mo |

## Dev Stack (`wos-dev`)

**Region:** `us-east-1`
**SAM config:** `infra/samconfig.toml` (default profile)

### Stack Outputs

| Key | Value |
|-----|-------|
| ApiUrl | `https://iofrdh7vgl.execute-api.us-east-1.amazonaws.com/dev` |
| CloudFrontUrl | `https://dzgkcezaf1dfv.cloudfront.net` |
| CloudFrontDistributionId | `EWE2LGBUHCEI1` |
| FrontendBucketName | `wos-frontend-dev-561893854848` |
| UserPoolId | `us-east-1_KIijngrGa` |
| UserPoolClientId | `10tkk4i6kfjmpjbvvctahugguf` |
| MainTableName | `wos-main-dev` |
| AdminTableName | `wos-admin-dev` |
| ReferenceTableName | `wos-reference-dev` |

## Live Stack (`wos-live`)

**Region:** `us-east-1`
**SAM config:** `infra/samconfig.toml` (`live` profile)

### Stack Outputs

| Key | Value |
|-----|-------|
| ApiUrl | `https://jbz4lfpfm5.execute-api.us-east-1.amazonaws.com/live` |
| CloudFrontUrl | `https://d28ng7lebb6pxf.cloudfront.net` |
| CloudFrontDistributionId | `E1AJ7LCWTU8ZMH` |
| FrontendBucketName | `wos-frontend-live-561893854848` |
| UserPoolId | `us-east-1_RmBIg1Flh` |
| UserPoolClientId | `76u9b76r2bbat6ve1e9g0qfolv` |
| MainTableName | `wos-main-live` |
| AdminTableName | `wos-admin-live` |
| ReferenceTableName | `wos-reference-live` |

## Lambda Functions

| Function | Purpose |
|----------|---------|
| AuthFunction | Login, register, token refresh, password reset |
| HeroesFunction | Hero CRUD, hero data |
| ProfilesFunction | User profile management |
| ChiefFunction | Chief gear and charms |
| RecommendFunction | Upgrade recommendations engine |
| AdvisorFunction | AI-powered advisor (Claude/OpenAI) |
| AdminFunction | Admin dashboard, user management, feature flags |
| GeneralFunction | Events, lineups, tips, combat guides, packs, inbox |
| ScheduledCleanupFunction | Daily data cleanup |
| UserMigrationFunction | Cognito user migration trigger |

## SSL Certificate

**ACM ARN:** `arn:aws:acm:us-east-1:561893854848:certificate/b188665f-fa56-4a14-a0e3-3b50a4b126e2`
**Domains:** `*.randomchaoslabs.com`, `randomchaoslabs.com`
**Validation:** DNS (auto-validated via Route 53)

## DNS (Route 53)

**Hosted Zone ID:** `Z072351926TTPYOWDY0N3`

| Domain | Type | Points To | Purpose |
|--------|------|-----------|---------|
| randomchaoslabs.com | A | 52.20.89.13 | Landing page (Lightsail) |
| www.randomchaoslabs.com | A | 52.20.89.13 | Landing page (Lightsail) |
| wos.randomchaoslabs.com | A (Alias) | d28ng7lebb6pxf.cloudfront.net | Live app (CloudFront) |
| wosdev.randomchaoslabs.com | A (Alias) | dzgkcezaf1dfv.cloudfront.net | Dev app (CloudFront) |

## Deployment Commands

### Prerequisites
- AWS SAM CLI installed
- AWS CLI configured with credentials
- Python 3.13+
- Node.js (for frontend build)

### Deploy to Dev
```bash
# Build and deploy backend
cd infra
sam build
sam deploy --no-confirm-changeset

# Build and deploy frontend
cd ../frontend
npm run build
aws s3 sync out s3://wos-frontend-dev-561893854848 --delete
aws cloudfront create-invalidation --distribution-id EWE2LGBUHCEI1 --paths "/*"
```

### Deploy to Live
```bash
# Build and deploy backend
cd infra
sam build
sam deploy --config-env live --no-confirm-changeset

# Build and deploy frontend
cd ../frontend
npm run build
aws s3 sync out s3://wos-frontend-live-561893854848 --delete
aws cloudfront create-invalidation --distribution-id E1AJ7LCWTU8ZMH --paths "/*"
```

### View Lambda Logs
```bash
# Tail logs for a specific function
sam logs -n AuthFunction --stack-name wos-dev --tail

# Or via CloudWatch
aws logs tail /aws/lambda/wos-auth-dev --follow
```

### Check Stack Status
```bash
aws cloudformation describe-stacks --stack-name wos-dev --query "Stacks[0].{Status:StackStatus,Outputs:Outputs[*].{Key:OutputKey,Value:OutputValue}}" --output table
```

## DynamoDB

### Tables (per environment)
| Table | Purpose |
|-------|---------|
| wos-main-{stage} | Users, profiles, heroes, inventory |
| wos-admin-{stage} | Feature flags, announcements, feedback, AI conversations |
| wos-reference-{stage} | Static game data (heroes) |

### Scan a Table
```bash
aws dynamodb scan --table-name wos-main-dev --max-items 10 --output json
```

### Query by Partition Key
```bash
aws dynamodb query --table-name wos-main-dev --key-condition-expression "PK = :pk" --expression-attribute-values '{":pk":{"S":"USER#<user-id>"}}' --output json
```

## Cognito

### List Users
```bash
aws cognito-idp list-users --user-pool-id <pool-id> --output table
```

### Create Admin User (after fresh deploy)
```bash
python scripts/create_admin.py --stage dev --email adamkirschner@outlook.com
python scripts/create_admin.py --stage live --email adamkirschner@outlook.com
```

## Seed Reference Data (after fresh deploy)
```bash
python scripts/seed_reference_data.py --stage dev
python scripts/seed_reference_data.py --stage live
```

## Secrets Manager

API keys for AI providers are stored in Secrets Manager:
- Dev: `wos/api-keys/dev`
- Live: `wos/api-keys/live`

```bash
# View current secrets
aws secretsmanager get-secret-value --secret-id wos/api-keys/dev --query SecretString --output text

# Update secrets
aws secretsmanager update-secret --secret-id wos/api-keys/live --secret-string '{"ANTHROPIC_API_KEY":"","OPENAI_API_KEY":"sk-..."}'
```

## CloudFront

### Invalidate Cache (after frontend deploy)
```bash
# Dev
aws cloudfront create-invalidation --distribution-id EWE2LGBUHCEI1 --paths "/*"

# Live
aws cloudfront create-invalidation --distribution-id E1AJ7LCWTU8ZMH --paths "/*"
```

## Email (AWS SES)

**Status:** Sandbox mode (can only send to verified emails)

SPF record: `"v=spf1 include:spf.improvmx.com include:amazonses.com ~all"`

```bash
# Verify an email for sandbox testing
aws ses verify-email-identity --email-address user@example.com

# List verified emails
aws ses list-identities --identity-type EmailAddress

# Check sending limits
aws ses get-send-quota
```

To send to any email: request production access via AWS Console → SES → Account dashboard.

## Fresh Deploy Checklist

After deploying a new stack from scratch:

1. `sam build && sam deploy` (or `--config-env live`)
2. `python scripts/seed_reference_data.py --stage <stage>` (load heroes)
3. `python scripts/create_admin.py --stage <stage> --email <email>` (bootstrap admin)
4. Build and deploy frontend to S3
5. Invalidate CloudFront cache
6. Set API keys in Secrets Manager
7. Update DNS in Route 53 if needed
8. Feature flags and AI settings auto-seed on first admin API call
