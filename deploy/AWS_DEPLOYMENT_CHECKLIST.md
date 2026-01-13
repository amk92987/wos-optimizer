# AWS Deployment Checklist - Bear's Den

Master checklist for deploying to AWS. Work through each phase in order.

**Status Legend:**
- [ ] Not started
- [~] In progress
- [x] Complete
- [!] Blocked/Issue

---

## Phase 0: Pre-Requisites

### Things You Need Before Starting
- [ ] AWS Account created (https://aws.amazon.com)
- [ ] Credit card on file with AWS
- [ ] Domain name purchased (randomchaoslabs.com?)
- [ ] GitHub repo with latest code pushed
- [ ] Anthropic or OpenAI API key for AI features
- [ ] Ko-fi account set up for donations

### Local Testing Complete
- [ ] App runs locally with `streamlit run app.py`
- [ ] Docker build works: `docker-compose up --build`
- [ ] Can login/register users locally
- [ ] Hero tracker works
- [ ] AI Advisor works (with API key)
- [ ] All pages load without errors

---

## Phase 1: AWS Account Security (Do First!)

### 1.1 Root Account Security
- [ ] Log into AWS Console as root
- [ ] Enable MFA on root account
  - Security Credentials → MFA → Activate MFA
  - Use authenticator app (Google Authenticator, Authy)
  - **Save backup codes somewhere safe!**
- [ ] Set strong password on root account

### 1.2 Create IAM Admin User
- [ ] Go to IAM → Users → Create User
- [ ] Username: `adam-admin` (or your name)
- [ ] Enable console access
- [ ] Set custom password
- [ ] Attach policy: `AdministratorAccess`
- [ ] Enable MFA on this user too
- [ ] **Log out of root, log in as IAM user**
- [ ] Bookmark IAM login URL: `https://<account-id>.signin.aws.amazon.com/console`

### 1.3 Billing Alerts
- [ ] Go to Billing → Budgets → Create Budget
- [ ] Create budget: $25/month (alert at 80%, 100%)
- [ ] Create budget: $50/month (alert at 100%)
- [ ] Verify email alerts are working
- [ ] Enable Cost Explorer (Billing → Cost Explorer → Enable)

### 1.4 Region Selection
- [ ] Choose your primary region: _____________
  - Recommended: `us-east-1` (cheapest, most services)
  - If targeting specific geography, pick closest region
- [ ] **Stick to ONE region** (multi-region = complexity + cost)

---

## Phase 2: Network Setup (VPC)

### 2.1 Use Default VPC (Simplest)
- [ ] Go to VPC → Your VPCs
- [ ] Confirm default VPC exists
- [ ] Note the VPC ID: `vpc-_____________`
- [ ] Note available subnets (need at least 2 for RDS)
  - Subnet 1: `subnet-_____________` (AZ: _____)
  - Subnet 2: `subnet-_____________` (AZ: _____)

### 2.2 Security Groups
- [ ] Create security group: `bearsden-web`
  - VPC: Default VPC
  - Inbound rules:
    - SSH (22) from My IP only
    - HTTP (80) from Anywhere (0.0.0.0/0)
    - HTTPS (443) from Anywhere (0.0.0.0/0)
  - Outbound: All traffic (default)
  - Note SG ID: `sg-_____________`

- [ ] Create security group: `bearsden-db`
  - VPC: Default VPC
  - Inbound rules:
    - PostgreSQL (5432) from `bearsden-web` security group only
  - Outbound: All traffic (default)
  - Note SG ID: `sg-_____________`

---

## Phase 3: Database Setup (RDS)

### 3.1 Create Subnet Group
- [ ] Go to RDS → Subnet Groups → Create
- [ ] Name: `bearsden-db-subnet`
- [ ] VPC: Default VPC
- [ ] Add subnets from at least 2 AZs
- [ ] Create subnet group

### 3.2 Create Sandbox Database (For Testing)
- [ ] Go to RDS → Create Database
- [ ] Engine: PostgreSQL
- [ ] Version: 15.x (or latest)
- [ ] Template: Free tier (if available) or Dev/Test
- [ ] DB Instance Identifier: `bearsden-sandbox`
- [ ] Master username: `wos_admin`
- [ ] Master password: _____________ (save this!)
- [ ] Instance class: db.t3.micro
- [ ] Storage: 20 GB, GP3
- [ ] Multi-AZ: NO (not needed for sandbox)
- [ ] VPC: Default VPC
- [ ] Subnet group: bearsden-db-subnet
- [ ] Public access: No
- [ ] Security group: bearsden-db
- [ ] Initial database name: `wos_sandbox`
- [ ] Backup retention: 7 days
- [ ] Create database
- [ ] Wait for status: Available (~10 min)
- [ ] Note endpoint: `bearsden-sandbox.___________.rds.amazonaws.com`

### 3.3 Create Production Database
- [ ] Same as above but:
- [ ] DB Instance Identifier: `bearsden-production`
- [ ] Instance class: db.t3.small (more memory)
- [ ] Storage: 50 GB
- [ ] Initial database name: `wos_production`
- [ ] Backup retention: 30 days
- [ ] Enable deletion protection: YES
- [ ] Enable storage encryption: YES
- [ ] Note endpoint: `bearsden-production.___________.rds.amazonaws.com`

### 3.4 Test Database Connection
- [ ] From local machine (temporarily allow your IP in security group)
- [ ] Or wait until EC2 is set up and test from there

---

## Phase 4: EC2 Instance Setup

### 4.1 Create Key Pair
- [ ] Go to EC2 → Key Pairs → Create
- [ ] Name: `bearsden-key`
- [ ] Type: RSA
- [ ] Format: .pem (Mac/Linux) or .ppk (Windows/PuTTY)
- [ ] Download and save securely: `bearsden-key.pem`
- [ ] **DO NOT LOSE THIS FILE**

### 4.2 Launch EC2 Instance
- [ ] Go to EC2 → Instances → Launch Instance
- [ ] Name: `bearsden-app`
- [ ] AMI: Ubuntu Server 22.04 LTS (64-bit x86)
- [ ] Instance type: t3.small
- [ ] Key pair: bearsden-key
- [ ] Network settings:
  - VPC: Default VPC
  - Subnet: Any public subnet
  - Auto-assign public IP: Enable
  - Security group: Select existing → bearsden-web
- [ ] Storage: 30 GB GP3
- [ ] Launch instance
- [ ] Wait for status: Running
- [ ] Note Public IP: _____________
- [ ] Note Instance ID: `i-_____________`

### 4.3 Allocate Elastic IP (Static IP)
- [ ] Go to EC2 → Elastic IPs → Allocate
- [ ] Allocate Elastic IP address
- [ ] Associate with bearsden-app instance
- [ ] Note Elastic IP: _____________
- [ ] **This IP won't change when you restart the instance**

### 4.4 Connect to Instance
```bash
# Set key permissions (Mac/Linux)
chmod 400 bearsden-key.pem

# Connect
ssh -i bearsden-key.pem ubuntu@<elastic-ip>
```
- [ ] Successfully connected via SSH

### 4.5 Install Docker on EC2
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
sudo apt install -y docker.io docker-compose-v2

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker ubuntu

# IMPORTANT: Log out and back in
exit
```
- [ ] Reconnect via SSH
- [ ] Verify docker works: `docker --version`
- [ ] Verify docker-compose works: `docker compose version`

---

## Phase 5: First Deployment (Basic)

### 5.1 Clone Repository
```bash
cd ~
git clone https://github.com/YOUR_USERNAME/WoS.git
cd WoS
```
- [ ] Repository cloned successfully

### 5.2 Create Environment File
```bash
cat > .env << 'EOF'
ENVIRONMENT=production
DEV_AUTO_LOGIN=false
SECRET_KEY=<generate-random-string>
ANTHROPIC_API_KEY=<your-key>
DATABASE_URL=postgresql://wos_admin:<password>@<rds-endpoint>:5432/wos_production
EOF
```
- [ ] .env file created
- [ ] SECRET_KEY set (use: `openssl rand -hex 32`)
- [ ] API key added
- [ ] DATABASE_URL configured with RDS endpoint

### 5.3 Build and Start
```bash
cd deploy
docker compose up -d --build
```
- [ ] Build completes without errors
- [ ] Containers start successfully
- [ ] Check status: `docker compose ps`
- [ ] Check logs: `docker compose logs -f`

### 5.4 Verify Deployment
```bash
# Health check
curl http://localhost/_stcore/health

# Check from browser
# http://<elastic-ip>
```
- [ ] Health check returns OK
- [ ] Landing page loads in browser
- [ ] Can access login page
- [ ] Can create new account
- [ ] Can log in
- [ ] Hero tracker works
- [ ] AI Advisor works

---

## Phase 6: Domain & SSL

### 6.1 DNS Configuration
**Option A: Using Route 53**
- [ ] Go to Route 53 → Hosted Zones → Create
- [ ] Domain name: randomchaoslabs.com
- [ ] Note nameservers (NS records)
- [ ] Update domain registrar to use Route 53 nameservers
- [ ] Create A record: @ → Elastic IP
- [ ] Create A record: www → Elastic IP

**Option B: Using External DNS (Namecheap, GoDaddy, etc.)**
- [ ] Log into domain registrar
- [ ] Create A record: @ → Elastic IP
- [ ] Create A record: www → Elastic IP

- [ ] Wait for DNS propagation (~5-30 minutes)
- [ ] Test: `nslookup randomchaoslabs.com`
- [ ] Test: Visit http://randomchaoslabs.com

### 6.2 SSL Certificate (Let's Encrypt)
```bash
# SSH into EC2
ssh -i bearsden-key.pem ubuntu@<elastic-ip>

# Install certbot
sudo apt install -y certbot

# Stop nginx temporarily
cd ~/WoS/deploy
docker compose stop nginx

# Get certificate
sudo certbot certonly --standalone \
  -d randomchaoslabs.com \
  -d www.randomchaoslabs.com \
  --email your@email.com \
  --agree-tos

# Copy certificates
sudo mkdir -p ~/WoS/deploy/ssl
sudo cp /etc/letsencrypt/live/randomchaoslabs.com/fullchain.pem ~/WoS/deploy/ssl/
sudo cp /etc/letsencrypt/live/randomchaoslabs.com/privkey.pem ~/WoS/deploy/ssl/
sudo chown -R ubuntu:ubuntu ~/WoS/deploy/ssl/
```
- [ ] Certificate obtained successfully
- [ ] Certificates copied to deploy/ssl/

### 6.3 Enable HTTPS
- [ ] Edit `docker-compose.yml`:
  - Change nginx config to `nginx-ssl.conf`
  - Add volume mount for ssl directory
  - Add port 443 mapping
- [ ] Restart: `docker compose up -d`
- [ ] Test: https://randomchaoslabs.com
- [ ] Verify redirect: http → https

### 6.4 Auto-Renewal Setup
```bash
# Create renewal script
sudo cat > /etc/cron.d/certbot-renew << 'EOF'
0 0 1 * * root certbot renew --quiet --post-hook "cp /etc/letsencrypt/live/randomchaoslabs.com/*.pem /home/ubuntu/WoS/deploy/ssl/ && docker compose -f /home/ubuntu/WoS/deploy/docker-compose.yml restart nginx"
EOF
```
- [ ] Cron job created for auto-renewal

---

## Phase 7: Database Migration (SQLite → PostgreSQL)

### 7.1 Export Data from Local SQLite
```bash
# On your LOCAL machine
cd WoS

# Create export script (we'll create this)
python scripts/export_data.py --output data_export.json
```
- [ ] Export script created
- [ ] Data exported successfully
- [ ] Verify export file contains all data

### 7.2 Initialize Production Database
```bash
# On EC2
cd ~/WoS

# Run migrations
docker compose exec app python -c "from database.db import init_db; init_db()"
```
- [ ] Tables created in PostgreSQL

### 7.3 Import Data to Production
```bash
# Copy export to EC2
scp -i bearsden-key.pem data_export.json ubuntu@<elastic-ip>:~/WoS/

# Import
docker compose exec app python scripts/import_data.py --input data_export.json
```
- [ ] Import script created
- [ ] Data imported successfully
- [ ] Verify data in production

### 7.4 Verify Data Integrity
- [ ] Log in as existing user
- [ ] Check profile data correct
- [ ] Check heroes are intact
- [ ] Check all settings preserved

---

## Phase 8: Production Hardening

### 8.1 Security Checklist
- [ ] DEV_AUTO_LOGIN=false verified
- [ ] Default admin password changed (admin/admin123 → new password)
- [ ] Security group rules are minimal
- [ ] SSH only from known IPs
- [ ] Database not publicly accessible

### 8.2 Performance Tuning
- [ ] Review Streamlit settings in docker-compose.yml
- [ ] Set appropriate worker count
- [ ] Configure nginx caching for static files

### 8.3 Error Handling
- [ ] Custom error pages configured
- [ ] Application logs being captured
- [ ] No sensitive info in error messages

---

## Phase 9: Monitoring & Backups

### 9.1 CloudWatch Setup
- [ ] Go to CloudWatch → Alarms → Create
- [ ] Create alarm: EC2 CPU > 80%
- [ ] Create alarm: EC2 Status Check Failed
- [ ] Create alarm: RDS CPU > 80%
- [ ] Create alarm: RDS Storage < 20%
- [ ] Configure SNS topic for email alerts
- [ ] Test alert delivery

### 9.2 RDS Backup Verification
- [ ] Verify automated backups enabled
- [ ] Note backup window: _____________
- [ ] Test manual snapshot creation
- [ ] Test restore from snapshot (to a test instance)
- [ ] Delete test instance after verification

### 9.3 Application Backup
```bash
# Create backup script
cat > ~/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d)
# Backup application files
tar -czf ~/backups/app-$DATE.tar.gz ~/WoS
# Keep last 7 days
find ~/backups -name "app-*.tar.gz" -mtime +7 -delete
EOF
chmod +x ~/backup.sh

# Add to crontab
crontab -e
# Add: 0 2 * * * /home/ubuntu/backup.sh
```
- [ ] Backup script created
- [ ] Cron job configured
- [ ] Test backup runs successfully

### 9.4 Uptime Monitoring
- [ ] Set up external monitoring (UptimeRobot, Pingdom, or similar)
- [ ] Monitor: https://randomchaoslabs.com/healthz
- [ ] Configure alerts for downtime
- [ ] Test alert by stopping container temporarily

---

## Phase 10: Go Live!

### 10.1 Final Testing
- [ ] Full user journey test:
  - [ ] Visit landing page
  - [ ] Register new account
  - [ ] Log in
  - [ ] Complete settings
  - [ ] Add heroes
  - [ ] Use AI Advisor
  - [ ] Log out
  - [ ] Log back in
  - [ ] Data persisted correctly

### 10.2 Performance Test
- [ ] Page load time < 3 seconds
- [ ] AI responses working
- [ ] No console errors in browser

### 10.3 Launch Tasks
- [ ] Announce on Discord/social media
- [ ] Monitor closely for first 24 hours
- [ ] Check CloudWatch for any issues
- [ ] Check error logs frequently

---

## Phase 11: Post-Launch

### 11.1 First Week Monitoring
- [ ] Check logs daily
- [ ] Monitor costs in AWS Console
- [ ] Watch for any user-reported issues
- [ ] Check database size/performance

### 11.2 Ongoing Maintenance Schedule

**Daily:**
- [ ] Check CloudWatch alarms
- [ ] Review error logs

**Weekly:**
- [ ] Check AWS costs
- [ ] Review user feedback
- [ ] Check disk space

**Monthly:**
- [ ] Review and apply security updates
- [ ] Check SSL certificate expiry
- [ ] Review and clean old backups
- [ ] Cost optimization review

---

## Reference Information

### Important URLs
| Resource | URL |
|----------|-----|
| AWS Console | https://console.aws.amazon.com |
| App (Production) | https://randomchaoslabs.com |
| EC2 Instance | i-_________________ |
| RDS Sandbox | bearsden-sandbox.____________.rds.amazonaws.com |
| RDS Production | bearsden-production.____________.rds.amazonaws.com |

### Important Credentials (Store Securely!)
| Credential | Location |
|------------|----------|
| AWS Root Password | _________________ |
| AWS IAM Password | _________________ |
| RDS Master Password | _________________ |
| SSH Key File | _________________ |
| SSL Certificate | /home/ubuntu/WoS/deploy/ssl/ |

### Key Commands
```bash
# SSH to server
ssh -i bearsden-key.pem ubuntu@<elastic-ip>

# View logs
cd ~/WoS/deploy && docker compose logs -f

# Restart app
cd ~/WoS/deploy && docker compose restart app

# Full restart
cd ~/WoS/deploy && docker compose down && docker compose up -d

# Update deployment
cd ~/WoS && git pull && cd deploy && docker compose up -d --build

# Database backup (manual snapshot)
aws rds create-db-snapshot \
  --db-instance-identifier bearsden-production \
  --db-snapshot-identifier manual-$(date +%Y%m%d)
```

### Emergency Contacts
- AWS Support: https://console.aws.amazon.com/support
- Domain Registrar: _________________

---

## Rollback Procedures

### If Deployment Fails
```bash
# 1. Check what's wrong
docker compose logs app

# 2. Rollback to previous code
cd ~/WoS
git log --oneline -5  # Find last working commit
git checkout <commit-hash>
cd deploy
docker compose up -d --build
```

### If Database Corrupted
```bash
# 1. Stop application
cd ~/WoS/deploy
docker compose stop app

# 2. Restore from snapshot (AWS Console)
# RDS → Snapshots → Select snapshot → Restore

# 3. Update .env with new endpoint
# 4. Restart application
docker compose start app
```

---

## Notes & Issues Log

*Record any issues encountered and how they were resolved:*

| Date | Issue | Resolution |
|------|-------|------------|
| | | |
| | | |
| | | |

---

**Checklist Version:** 1.0
**Last Updated:** January 2026
**Estimated Time:** 4-8 hours (spread across multiple sessions)
