---
name: wos-deploy
description: Handle safe deployments to dev and live AWS environments. Includes pre-deployment checks, SAM build/deploy, S3 sync, and CloudFront invalidation. Use when deploying changes.
allowed-tools: Bash, Read, Glob
---

# WoS Deployment Agent - Safe AWS Deployments

## Purpose
Manages deployments to dev and live AWS environments with pre-deployment validation, backend (SAM/Lambda) and frontend (S3/CloudFront) deployment steps, and post-deployment verification.

## When to Use
- Deploying backend changes (Lambda handlers, common layer, SAM template)
- Deploying frontend changes (Next.js static export to S3)
- Full stack deployments (backend + frontend)
- Checking deployment status or troubleshooting failed deploys

## Environment Reference

| Resource | Dev | Live |
|----------|-----|------|
| SAM Stack | `wos-dev` | `wos-live` |
| SAM Config | `default` profile | `live` profile |
| API Gateway | `iofrdh7vgl.execute-api.us-east-1.amazonaws.com/dev` | `jbz4lfpfm5.execute-api.us-east-1.amazonaws.com/live` |
| S3 Frontend | `wos-frontend-dev-561893854848` | `wos-frontend-live-561893854848` |
| CloudFront ID | `EWE2LGBUHCEI1` | `E1AJ7LCWTU8ZMH` |
| CloudFront URL | `wosdev.randomchaoslabs.com` | `wos.randomchaoslabs.com` |
| DynamoDB Main | `wos-main-dev` | `wos-main-live` |
| DynamoDB Admin | `wos-admin-dev` | `wos-admin-live` |
| DynamoDB Reference | `wos-reference-dev` | `wos-reference-live` |
| Cognito Pool | `us-east-1_KIijngrGa` | `us-east-1_RmBIg1Flh` |

### Tool Paths (Windows)
```
SAM CLI: "C:\Program Files\Amazon\AWSSAMCLI\bin\sam.cmd"
AWS CLI: "C:\Program Files\Amazon\AWSCLIV2\aws.exe"
Python: C:\Users\adam\AppData\Local\Programs\Python\Python313
Project: C:\Users\adam\IdeaProjects\wos-optimizer
```

## Deployment Options

### Option 1: PowerShell Deploy Script (Recommended for Dev)
```powershell
# Full deploy (backend + frontend)
powershell -File C:\Users\adam\IdeaProjects\wos-optimizer\scripts\deploy_dev.ps1

# Backend only
powershell -File C:\Users\adam\IdeaProjects\wos-optimizer\scripts\deploy_dev.ps1 -BackendOnly

# Frontend only (requires pre-built output in frontend/out/)
powershell -File C:\Users\adam\IdeaProjects\wos-optimizer\scripts\deploy_dev.ps1 -FrontendOnly
```

### Option 2: Manual Step-by-Step

#### Backend Deploy (Dev)
```bash
cd /c/Users/adam/IdeaProjects/wos-optimizer/infra
"C:\Program Files\Amazon\AWSSAMCLI\bin\sam.cmd" build
"C:\Program Files\Amazon\AWSSAMCLI\bin\sam.cmd" deploy --no-confirm-changeset
```

#### Backend Deploy (Live)
```bash
cd /c/Users/adam/IdeaProjects/wos-optimizer/infra
"C:\Program Files\Amazon\AWSSAMCLI\bin\sam.cmd" build
"C:\Program Files\Amazon\AWSSAMCLI\bin\sam.cmd" deploy --config-env live --no-confirm-changeset
```

#### Frontend Build
```bash
cd /c/Users/adam/IdeaProjects/wos-optimizer/frontend
npm run build
```

#### Frontend Deploy (Dev)
```bash
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" s3 sync C:\Users\adam\IdeaProjects\wos-optimizer\frontend\out s3://wos-frontend-dev-561893854848 --delete --region us-east-1
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" cloudfront create-invalidation --distribution-id EWE2LGBUHCEI1 --paths "/*" --region us-east-1
```

#### Frontend Deploy (Live)
```bash
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" s3 sync C:\Users\adam\IdeaProjects\wos-optimizer\frontend\out s3://wos-frontend-live-561893854848 --delete --region us-east-1
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" cloudfront create-invalidation --distribution-id E1AJ7LCWTU8ZMH --paths "/*" --region us-east-1
```

## Pre-Deployment Checklist

### Always Check Before Deploying

1. **Git status is clean** (or changes are committed)
   ```bash
   cd /c/Users/adam/IdeaProjects/wos-optimizer && git status
   ```

2. **Backend data files in sync** - Two copies must match:
   - `data/heroes.json` (source of truth)
   - `backend/data/heroes.json` (bundled with Lambda)
   ```bash
   diff /c/Users/adam/IdeaProjects/wos-optimizer/data/heroes.json /c/Users/adam/IdeaProjects/wos-optimizer/backend/data/heroes.json
   ```

3. **Frontend builds successfully**
   ```bash
   cd /c/Users/adam/IdeaProjects/wos-optimizer/frontend && npm run build
   ```

4. **SAM template validates**
   ```bash
   cd /c/Users/adam/IdeaProjects/wos-optimizer/infra && "C:\Program Files\Amazon\AWSSAMCLI\bin\sam.cmd" validate
   ```

5. **No secrets in committed files**
   ```bash
   cd /c/Users/adam/IdeaProjects/wos-optimizer && git diff --cached --name-only | grep -E '\.env|credentials|secret'
   ```

### Additional Checks for Live Deployments

6. **Changes tested on dev first** - Verify the same changes are working on `wosdev.randomchaoslabs.com`

7. **No destructive database changes** - Check if SAM template modifies DynamoDB tables with `DeletionPolicy: Retain`

8. **API backwards compatibility** - New API fields should be optional; don't remove existing fields

9. **Feature flags** - New features should be behind feature flags on initial live deploy

## Post-Deployment Verification

### Check Backend Health
```bash
# Dev
curl -s https://iofrdh7vgl.execute-api.us-east-1.amazonaws.com/dev/health | python -m json.tool

# Live
curl -s https://jbz4lfpfm5.execute-api.us-east-1.amazonaws.com/live/health | python -m json.tool
```

### Check Frontend Loads
```bash
# Dev
curl -s -o /dev/null -w "%{http_code}" https://wosdev.randomchaoslabs.com

# Live
curl -s -o /dev/null -w "%{http_code}" https://wos.randomchaoslabs.com
```

### Check CloudFront Invalidation Status
```bash
# Dev
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" cloudfront list-invalidations --distribution-id EWE2LGBUHCEI1 --max-items 3 --region us-east-1

# Live
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" cloudfront list-invalidations --distribution-id E1AJ7LCWTU8ZMH --max-items 3 --region us-east-1
```

### Check Lambda Function Logs (recent errors)
```bash
# Check for recent errors in any Lambda function (dev)
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" logs filter-log-events \
  --log-group-name "/aws/lambda/wos-dev-HeroesFunction-*" \
  --filter-pattern "ERROR" \
  --start-time $(date -d '10 minutes ago' +%s000) \
  --region us-east-1
```

## SAM Configuration

SAM config is in `infra/samconfig.toml`:
- `[default]` profile = dev environment
- `[live]` profile = live environment
- Both use `resolve_s3 = true` (auto-create deployment S3 bucket)
- Both use `cached = true` and `parallel = true` for builds

Key SAM template parameters:
- `Stage` - `dev` or `live`
- `CertificateArn` - ACM wildcard cert for custom domains
- `ExistingUserPoolId` / `ExistingUserPoolClientId` - Reuse existing Cognito pools

## Troubleshooting

### SAM Build Fails
- Check Python is on PATH: `python --version` should show 3.13+
- PowerShell script prepends Python to PATH automatically
- Clear cache: delete `infra/.aws-sam/` directory and rebuild

### SAM Deploy Fails
- Check CloudFormation console for detailed error messages
- Common: IAM permission changes need `CAPABILITY_IAM`
- Rollback: CloudFormation auto-rolls back failed deployments

### Frontend Build Fails
- Check Node version: `node --version` (need 18+)
- Clear Next.js cache: delete `frontend/.next/` and rebuild
- Check environment variables in `frontend/.env.production` or `.env.development`

### CloudFront 403/404 After Deploy
- S3 bucket policy may need updating
- CloudFront origin access identity (OAI) permissions
- Check the URL rewrite function: `infra/url-rewrite.js`

### API Returns 500
- Check Lambda CloudWatch logs
- Common: missing environment variables in SAM template
- Common: DynamoDB permission issues (check IAM role)

## Safety Rules

1. **NEVER deploy to live without testing on dev first**
2. **ALWAYS confirm with user before live deployments**
3. **ALWAYS run pre-deployment checklist**
4. **ALWAYS check data file sync** (data/ vs backend/data/)
5. **Keep SAM template's DeletionPolicy: Retain** on DynamoDB tables
6. **Monitor CloudWatch** after live deployments for errors
7. **Have a rollback plan** - CloudFormation supports automatic rollback

## Workflow

1. **Determine scope** - Backend, frontend, or both? Dev or live?
2. **Run pre-deployment checks** - Git status, data sync, builds
3. **Deploy backend** (if needed) - SAM build + deploy
4. **Deploy frontend** (if needed) - npm build + S3 sync + CloudFront invalidation
5. **Post-deployment verify** - Health check, error logs
6. **Report results** - Deployment status summary
