# Deployment Guide

## AWS CLI

**Path:** `"C:\Program Files\Amazon\AWSCLIV2\aws.exe"`

**SSH Key:** `C:\Users\adam\.ssh\lightsail-key.pem`

## Environments

| Name | Instance | IP | URL | Database | Cost |
|------|----------|-----|-----|----------|------|
| **Local** | Your machine | localhost:8501 | N/A | SQLite (wos.db) | Free |
| **Dev** | wos-dev-micro | 98.87.57.79 | wosdev.randomchaoslabs.com | PostgreSQL | $7/mo |
| **Live** | wos-live-micro | 52.55.47.124 | wos.randomchaoslabs.com | PostgreSQL | $7/mo |
| **Landing** | randomchaoslabs-server | 52.20.89.13 | www.randomchaoslabs.com | N/A | $5/mo |

## DNS (Route 53)

**Hosted Zone ID:** `Z072351926TTPYOWDY0N3`

| Domain | Type | Points To | Purpose |
|--------|------|-----------|---------|
| randomchaoslabs.com | A | 52.20.89.13 | Landing page |
| www.randomchaoslabs.com | A | 52.20.89.13 | Landing page |
| wos.randomchaoslabs.com | A | 52.55.47.124 | Live app |
| wosapp.randomchaoslabs.com | A | 52.55.47.124 | Live app (alias) |
| wosdev.randomchaoslabs.com | A | 98.87.57.79 | Dev app |

### Update DNS Record
```bash
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" route53 change-resource-record-sets --hosted-zone-id Z072351926TTPYOWDY0N3 --change-batch "{\"Changes\":[{\"Action\":\"UPSERT\",\"ResourceRecordSet\":{\"Name\":\"<subdomain>.randomchaoslabs.com\",\"Type\":\"A\",\"TTL\":300,\"ResourceRecords\":[{\"Value\":\"<ip-address>\"}]}}]}"
```

### List All DNS Records
```bash
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" route53 list-resource-record-sets --hosted-zone-id Z072351926TTPYOWDY0N3 --output table
```

## Lightsail Instances

| Instance | Bundle | RAM | Static IP |
|----------|--------|-----|-----------|
| wos-dev-micro | micro_3_0 | 1 GB | wos-dev-ip (98.87.57.79) |
| wos-live-micro | micro_3_0 | 1 GB | wos-live-ip (52.55.47.124) |
| randomchaoslabs-server | nano_3_0 | 0.5 GB | randomchaoslabs-ip (52.20.89.13) |

### Bundle Sizes
| Bundle | RAM | vCPU | Storage | Cost |
|--------|-----|------|---------|------|
| nano_3_0 | 0.5 GB | 1 | 20 GB | $5/mo |
| micro_3_0 | 1 GB | 1 | 40 GB | $7/mo |
| small_3_0 | 2 GB | 1 | 60 GB | $12/mo |
| medium_3_0 | 4 GB | 2 | 80 GB | $24/mo |

## Common Commands

### Check Instance Status
```bash
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" lightsail get-instance --instance-name wos-dev-micro
```

### List All Instances
```bash
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" lightsail get-instances --query "instances[].{name:name,state:state.name,ip:publicIpAddress,bundle:bundleId}" --output table
```

### Deploy to Dev
```bash
ssh -i "C:\Users\adam\.ssh\lightsail-key.pem" ubuntu@98.87.57.79 "cd /home/ubuntu/wos-app && git pull && sudo systemctl restart streamlit"
```

### Deploy to Live
```bash
ssh -i "C:\Users\adam\.ssh\lightsail-key.pem" ubuntu@52.55.47.124 "cd /home/ubuntu/wos-app && git pull && sudo systemctl restart streamlit"
```

### View Logs (Dev)
```bash
ssh -i "C:\Users\adam\.ssh\lightsail-key.pem" ubuntu@98.87.57.79 "sudo journalctl -u streamlit -f"
```

### View Logs (Live)
```bash
ssh -i "C:\Users\adam\.ssh\lightsail-key.pem" ubuntu@52.55.47.124 "sudo journalctl -u streamlit -f"
```

### Restart Service (Dev)
```bash
ssh -i "C:\Users\adam\.ssh\lightsail-key.pem" ubuntu@98.87.57.79 "sudo systemctl restart streamlit"
```

### Restart Service (Live)
```bash
ssh -i "C:\Users\adam\.ssh\lightsail-key.pem" ubuntu@52.55.47.124 "sudo systemctl restart streamlit"
```

### SSH to Dev
```bash
ssh -i "C:\Users\adam\.ssh\lightsail-key.pem" ubuntu@98.87.57.79
```

### SSH to Live
```bash
ssh -i "C:\Users\adam\.ssh\lightsail-key.pem" ubuntu@52.55.47.124
```

## Snapshot & Instance Management

### Create Snapshot
```bash
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" lightsail create-instance-snapshot --instance-name wos-dev-micro --instance-snapshot-name <snapshot-name>
```

### Create Instance from Snapshot
```bash
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" lightsail create-instances-from-snapshot --instance-names <new-instance-name> --availability-zone us-east-1a --bundle-id micro_3_0 --instance-snapshot-name <snapshot-name>
```

### Delete Instance
```bash
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" lightsail delete-instance --instance-name <instance-name>
```

## Static IP Management

### Allocate New Static IP
```bash
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" lightsail allocate-static-ip --static-ip-name <ip-name>
```

### Attach Static IP to Instance
```bash
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" lightsail attach-static-ip --static-ip-name <ip-name> --instance-name <instance-name>
```

### Detach Static IP
```bash
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" lightsail detach-static-ip --static-ip-name <ip-name>
```

### List Static IPs
```bash
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" lightsail get-static-ips
```

## Service Configuration (on server)

**Service file:** `/etc/systemd/system/streamlit.service`

**Environment file:** `/home/ubuntu/wos-app/.env`

**App directory:** `/home/ubuntu/wos-app`

### Key Environment Variables
| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `ENVIRONMENT` | `production`, `sandbox`, or `development` |
| `EMAIL_MODE` | `smtp` or `debug` |
| `SMTP_HOST` | SES endpoint (email-smtp.us-east-1.amazonaws.com) |
| `SMTP_PORT` | 587 |
| `SMTP_USER` | SES SMTP username |
| `SMTP_PASSWORD` | SES SMTP password |
| `SMTP_FROM` | From email address |
| `SMTP_FROM_NAME` | From display name |

### Reload Service After Config Change
```bash
sudo systemctl daemon-reload
sudo systemctl restart streamlit
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
