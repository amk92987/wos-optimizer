# Deployment Guide

## AWS CLI

**Path:** `"C:\Program Files\Amazon\AWSCLIV2\aws.exe"`

**SSH Key:** `C:\Users\adam\.ssh\lightsail-key.pem` (for legacy Lightsail instances)

## Architecture Overview

The app is migrating from Streamlit on Lightsail to a **serverless stack** (SAM/CloudFormation):

| Layer | Service | Details |
|-------|---------|---------|
| Frontend | S3 + CloudFront | Next.js static export |
| API | API Gateway (HTTP) | Routes to Lambda functions |
| Backend | Lambda (Python 3.13) | 10 functions (Auth, Heroes, Profiles, Chief, Recommend, Advisor, Admin, General, Cleanup, UserMigration) |
| Database | DynamoDB | 3 tables (main, admin, reference) |
| Auth | Cognito | Email-based user pool |
| Secrets | Secrets Manager | API keys and sensitive config |
| Email | SES | Transactional emails |

## Environments

| Name | Type | URL | Database | Cost |
|------|------|-----|----------|------|
| **Local** | Your machine (localhost:3000) | N/A | Local/SQLite | Free |
| **Dev** | Serverless (SAM stack `wos-dev`) | wosdev.randomchaoslabs.com | DynamoDB | ~$0 at low traffic |
| **Live (Streamlit)** | Lightsail `wos-live-micro` | wos.randomchaoslabs.com | PostgreSQL | $7/mo |
| **Live (Serverless)** | SAM stack `wos-live` (not yet deployed) | wos.randomchaoslabs.com | DynamoDB | ~$0 at low traffic |
| **Landing** | Lightsail `randomchaoslabs-server` | www.randomchaoslabs.com | N/A | $5/mo |

**Migration plan:** Dev serverless is live. Once verified, deploy `wos-live` stack and point `wos.randomchaoslabs.com` to it, then shut down `wos-live-micro` Lightsail.

## Serverless Stack (Dev)

**Stack name:** `wos-dev`
**Region:** `us-east-1`
**Created:** 2026-02-03
**Branch:** `feature/aws-serverless`

### Stack Outputs

| Key | Value |
|-----|-------|
| ApiUrl | `https://qro6iih6oe.execute-api.us-east-1.amazonaws.com/dev` |
| CloudFrontUrl | `https://d3q6j2q80oj6gu.cloudfront.net` |
| CloudFrontDistributionId | `E1CU7UPD2I54BY` |
| FrontendBucketName | `wos-frontend-dev-561893854848` |
| UserPoolId | `us-east-1_KvZMywYFF` |
| UserPoolClientId | `52393513i04q1pe1rk61eqq5oh` |
| MainTableName | `wos-main-dev` |
| AdminTableName | `wos-admin-dev` |
| ReferenceTableName | `wos-reference-dev` |

### Lambda Functions

| Function | Purpose |
|----------|---------|
| AuthFunction | Login, register, token refresh, password reset |
| HeroesFunction | Hero CRUD, hero data |
| ProfilesFunction | User profile management |
| ChiefFunction | Chief gear and charms |
| RecommendFunction | Upgrade recommendations engine |
| AdvisorFunction | AI-powered advisor (Claude/OpenAI) |
| AdminFunction | Admin dashboard, user management, feature flags |
| GeneralFunction | Events, lineups, tips, combat guides, packs |
| ScheduledCleanupFunction | Periodic data cleanup |
| UserMigrationFunction | Cognito user migration trigger |

### SSL Certificate

**ACM ARN:** `arn:aws:acm:us-east-1:561893854848:certificate/b188665f-fa56-4a14-a0e3-3b50a4b126e2`
**Domains:** `*.randomchaoslabs.com`, `randomchaoslabs.com`
**Validation:** DNS (auto-validated via Route 53)
**Note:** Wildcard cert covers both `wosdev` and `wos` subdomains for future live cutover.

## DNS (Route 53)

**Hosted Zone ID:** `Z072351926TTPYOWDY0N3`

| Domain | Type | Points To | Purpose |
|--------|------|-----------|---------|
| randomchaoslabs.com | A | 52.20.89.13 | Landing page (Lightsail) |
| www.randomchaoslabs.com | A | 52.20.89.13 | Landing page (Lightsail) |
| wos.randomchaoslabs.com | A | 52.55.47.124 | Live Streamlit app (Lightsail) |
| wosapp.randomchaoslabs.com | A | 52.55.47.124 | Live Streamlit app alias (Lightsail) |
| wosdev.randomchaoslabs.com | A (Alias) | d3q6j2q80oj6gu.cloudfront.net | Dev serverless app (CloudFront) |

### Update DNS Record (Static IP)
```bash
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" route53 change-resource-record-sets --hosted-zone-id Z072351926TTPYOWDY0N3 --change-batch "{\"Changes\":[{\"Action\":\"UPSERT\",\"ResourceRecordSet\":{\"Name\":\"<subdomain>.randomchaoslabs.com\",\"Type\":\"A\",\"TTL\":300,\"ResourceRecords\":[{\"Value\":\"<ip-address>\"}]}}]}"
```

### Update DNS Record (CloudFront Alias)
```bash
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" route53 change-resource-record-sets --hosted-zone-id Z072351926TTPYOWDY0N3 --change-batch "{\"Changes\":[{\"Action\":\"UPSERT\",\"ResourceRecordSet\":{\"Name\":\"<subdomain>.randomchaoslabs.com\",\"Type\":\"A\",\"AliasTarget\":{\"HostedZoneId\":\"Z2FDTNDATAQYW2\",\"DNSName\":\"<cloudfront-domain>.cloudfront.net\",\"EvaluateTargetHealth\":false}}}]}"
```

### List All DNS Records
```bash
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" route53 list-resource-record-sets --hosted-zone-id Z072351926TTPYOWDY0N3 --output table
```

## Serverless Deployment Commands

### Prerequisites
- AWS SAM CLI installed
- AWS CLI configured with credentials
- Python 3.13+
- Node.js (for frontend build)

### Deploy Backend (SAM)
```bash
cd infra

# Build Lambda functions
sam build

# Deploy to dev (default profile)
sam deploy

# Deploy to live
sam deploy --config-env live
```

### Deploy Frontend
```bash
cd frontend

# Install dependencies
npm install

# Build static export
npm run build

# Upload to S3
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" s3 sync out/ s3://wos-frontend-dev-561893854848/ --delete

# Invalidate CloudFront cache
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" cloudfront create-invalidation --distribution-id E1CU7UPD2I54BY --paths "/*"
```

### View Lambda Logs
```bash
# Tail logs for a specific function (e.g., AuthFunction)
sam logs -n AuthFunction --stack-name wos-dev --tail

# Or via CloudWatch
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" logs tail /aws/lambda/wos-dev-AuthFunction --follow
```

### Check Stack Status
```bash
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" cloudformation describe-stacks --stack-name wos-dev --query "Stacks[0].{Status:StackStatus,Outputs:Outputs[*].{Key:OutputKey,Value:OutputValue}}" --output table
```

### List Stack Resources
```bash
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" cloudformation list-stack-resources --stack-name wos-dev --query "StackResourceSummaries[*].{LogicalId:LogicalResourceId,Type:ResourceType,Status:ResourceStatus}" --output table
```

## DynamoDB

### Tables
| Table | Purpose |
|-------|---------|
| wos-main-dev | Users, profiles, heroes, inventory |
| wos-admin-dev | Feature flags, announcements, feedback, AI conversations |
| wos-reference-dev | Static game data (heroes, events, guides) |

### Scan a Table
```bash
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" dynamodb scan --table-name wos-main-dev --max-items 10 --output json
```

### Query by Partition Key
```bash
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" dynamodb query --table-name wos-main-dev --key-condition-expression "PK = :pk" --expression-attribute-values "{\":pk\":{\"S\":\"USER#<user-id>\"}}" --output json
```

## Cognito

### User Pool: `us-east-1_KvZMywYFF`

### List Users
```bash
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" cognito-idp list-users --user-pool-id us-east-1_KvZMywYFF --output table
```

### Create Admin User
```bash
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" cognito-idp admin-create-user --user-pool-id us-east-1_KvZMywYFF --username admin@randomchaoslabs.com --user-attributes Name=email,Value=admin@randomchaoslabs.com Name=email_verified,Value=true --temporary-password <password>
```

### Disable/Enable User
```bash
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" cognito-idp admin-disable-user --user-pool-id us-east-1_KvZMywYFF --username <email>
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" cognito-idp admin-enable-user --user-pool-id us-east-1_KvZMywYFF --username <email>
```

## CloudFront

### Distribution: `E1CU7UPD2I54BY`

### Invalidate Cache (after frontend deploy)
```bash
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" cloudfront create-invalidation --distribution-id E1CU7UPD2I54BY --paths "/*"
```

### Check Distribution Status
```bash
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" cloudfront get-distribution --id E1CU7UPD2I54BY --query "Distribution.{Status:Status,Domain:DomainName,Aliases:DistributionConfig.Aliases.Items}" --output json
```

## Legacy Lightsail (Streamlit)

**Note:** The dev Lightsail instance (`wos-dev-micro`) was shut down on 2026-02-09. A final snapshot exists: `wos-dev-final-backup-20260208`. The live Streamlit instance remains until serverless goes live.

### Remaining Instances

| Instance | Bundle | RAM | Static IP | Status |
|----------|--------|-----|-----------|--------|
| wos-live-micro | micro_3_0 | 1 GB | wos-live-ip (52.55.47.124) | Running (Streamlit production) |
| randomchaoslabs-server | nano_3_0 | 0.5 GB | randomchaoslabs-ip (52.20.89.13) | Running (Landing page) |

### Deploy to Live (Streamlit)
```bash
ssh -i "C:\Users\adam\.ssh\lightsail-key.pem" ubuntu@52.55.47.124 "cd /home/ubuntu/wos-app && git pull && sudo systemctl restart streamlit"
```

### View Logs (Live Streamlit)
```bash
ssh -i "C:\Users\adam\.ssh\lightsail-key.pem" ubuntu@52.55.47.124 "sudo journalctl -u streamlit -f"
```

### SSH to Live
```bash
ssh -i "C:\Users\adam\.ssh\lightsail-key.pem" ubuntu@52.55.47.124
```

## Email (AWS SES)

Email is configured via AWS SES. DKIM records are set up in Route 53.

**Status:** Sandbox mode (can only send to verified emails)

SPF record: `"v=spf1 include:spf.improvmx.com include:amazonses.com ~all"`

### Verify an Email Address (for sandbox testing)
```bash
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" ses verify-email-identity --email-address user@example.com
```

### List Verified Emails
```bash
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" ses list-identities --identity-type EmailAddress
```

### Check SES Sending Limits
```bash
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" ses get-send-quota
```

### Request Production Access
To send to any email address, request production access via AWS Console:
SES → Account dashboard → Request production access

## Going Live Checklist

When ready to cut over `wos.randomchaoslabs.com` to serverless:

1. Deploy live SAM stack: `cd infra && sam deploy --config-env live`
2. Build and upload frontend to live S3 bucket
3. Add `wos.randomchaoslabs.com` as alternate domain on live CloudFront distribution (ACM cert already covers it)
4. Migrate user data from PostgreSQL to DynamoDB (use `scripts/migrate_data.py`)
5. Update Route 53: change `wos.randomchaoslabs.com` from A record (52.55.47.124) to CloudFront alias
6. Verify everything works
7. Snapshot and delete `wos-live-micro` Lightsail instance (saves $7/mo)
8. Release `wos-live-ip` static IP
