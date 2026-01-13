# AWS First-Timer Guide

## Before You Do Anything Else

### 1. Secure Your AWS Account (Do This First!)

```
[ ] Enable MFA on root account
    - AWS Console → Security credentials → MFA → Activate
    - Use Google Authenticator or Authy
    - THIS IS CRITICAL - compromised AWS accounts get crypto-mined

[ ] Create an IAM user for daily use
    - Never use root account for daily work
    - AWS Console → IAM → Users → Create user
    - Give it AdministratorAccess (for now)
    - Enable MFA on this user too

[ ] Set up billing alerts
    - AWS Console → Billing → Budgets → Create budget
    - Set alert at $20, $50, $100
    - You WILL forget something running and get a surprise bill
```

### 2. Common Expensive Mistakes (Avoid These!)

| Mistake | Cost | How to Avoid |
|---------|------|--------------|
| Leaving EC2 running | $15-100/mo | Use t3.micro (free tier) for testing |
| RDS Multi-AZ when not needed | +$25/mo | Start with single-AZ, upgrade later |
| NAT Gateway | $30+/mo | Use public subnets to start |
| Elastic IP not attached | $3.60/mo | Release unused Elastic IPs |
| Old snapshots accumulating | $5+/mo | Set lifecycle policies |
| Data transfer out | Variable | Stay in one region |

### 3. Free Tier Awareness

AWS Free Tier (first 12 months):
- EC2: 750 hours/month of t2.micro or t3.micro
- RDS: 750 hours/month of db.t2.micro or db.t3.micro
- S3: 5GB storage
- Data transfer: 15GB out/month

**After free tier expires, you WILL be charged!** Set calendar reminder for 11 months out.

---

## Recommended Learning Order

### Week 1: Local Docker Testing
Before touching AWS, make sure everything works locally:

```bash
# Test the full stack locally
cd deploy
docker-compose up --build

# Visit http://localhost
# Test login, registration, all features
# Fix any issues HERE, not in AWS
```

### Week 2: Simple AWS Deployment

**Start with the absolute minimum:**

1. **One EC2 instance** (t3.small, ~$15/mo)
   - Runs both app and database initially
   - SQLite is fine for <100 users
   - This is NOT production-ready but lets you learn

2. **Skip these for now:**
   - RDS (use SQLite first)
   - Load balancers
   - Auto-scaling
   - Multiple availability zones

### Week 3-4: Add Production Components

Only after basic deployment works:

1. **Add RDS PostgreSQL**
   - Migrate data from SQLite
   - Set up automated backups

2. **Add SSL/HTTPS**
   - Let's Encrypt (free) or ACM

3. **Set up monitoring**
   - CloudWatch basics
   - Health check alerts

---

## Step-by-Step First Deployment

### Step 1: Launch EC2 Instance

```
AWS Console → EC2 → Launch Instance

1. Name: bearsden-app
2. AMI: Ubuntu 22.04 LTS (free tier eligible)
3. Instance type: t3.small ($15/mo) or t3.micro (free tier)
4. Key pair: Create new → Download .pem file → SAVE THIS FILE
5. Network settings:
   - Allow SSH (port 22) from "My IP" only
   - Allow HTTP (port 80) from anywhere
   - Allow HTTPS (port 443) from anywhere
6. Storage: 20 GB gp3
7. Launch instance
```

### Step 2: Connect to Instance

```bash
# Make key file secure (required on Mac/Linux)
chmod 400 your-key.pem

# Connect
ssh -i your-key.pem ubuntu@<public-ip>

# If on Windows, use PuTTY or WSL
```

### Step 3: Install Docker

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
sudo apt install -y docker.io docker-compose

# Add yourself to docker group
sudo usermod -aG docker ubuntu

# Log out and back in
exit
# Reconnect via SSH
```

### Step 4: Deploy Application

```bash
# Clone your repo
git clone https://github.com/YOUR_USERNAME/WoS.git
cd WoS

# Create production environment file
cat > .env << 'EOF'
ENVIRONMENT=production
DEV_AUTO_LOGIN=false
SECRET_KEY=$(openssl rand -hex 32)
# Add your API key
ANTHROPIC_API_KEY=your-key-here
EOF

# Build and run
cd deploy
docker-compose up -d

# Check it's running
docker-compose ps
curl http://localhost/_stcore/health
```

### Step 5: Access Your App

1. Find your EC2 public IP in AWS Console
2. Visit `http://<public-ip>` in browser
3. You should see the landing page!

### Step 6: Set Up Domain (Optional but Recommended)

If you have a domain:

1. **Get Elastic IP** (so IP doesn't change on restart)
   - EC2 → Elastic IPs → Allocate → Associate with instance

2. **Point domain to IP**
   - In your domain registrar (GoDaddy, Namecheap, etc.)
   - Add A record: @ → your-elastic-ip
   - Add A record: www → your-elastic-ip

3. **Set up SSL** (after DNS propagates, ~30 min)
   ```bash
   # Install certbot
   sudo apt install -y certbot

   # Stop nginx temporarily
   cd ~/WoS/deploy
   docker-compose stop nginx

   # Get certificate
   sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

   # Copy certs
   sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ssl/
   sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ssl/
   sudo chown ubuntu:ubuntu ssl/*.pem

   # Use SSL nginx config
   # Edit docker-compose.yml to use nginx-ssl.conf

   docker-compose up -d
   ```

---

## When Things Go Wrong

### Can't Connect via SSH
- Check security group allows port 22 from your IP
- Your IP might have changed (update security group)
- Key file permissions wrong (chmod 400)

### App Not Loading
```bash
# Check containers running
docker-compose ps

# Check logs
docker-compose logs app
docker-compose logs nginx

# Restart everything
docker-compose down
docker-compose up -d
```

### Out of Disk Space
```bash
# Check disk usage
df -h

# Clean Docker
docker system prune -a
```

### Locked Out of AWS Console
- If MFA device lost, contact AWS support
- This is why you should have a backup MFA method

---

## Cost Control Tips

1. **Set billing alerts** (seriously, do this)

2. **Stop instances when not using**
   ```bash
   # From EC2 console: Actions → Instance State → Stop
   # Stopped instances don't charge for compute (just storage)
   ```

3. **Use AWS Cost Explorer**
   - Check weekly to understand your spend
   - AWS Console → Billing → Cost Explorer

4. **Reserved Instances** (later, if staying on AWS)
   - After 1-2 months, if happy with setup
   - 1-year reserved instance saves ~30%

---

## Simpler Alternatives (Recommended for First-Timers)

### Railway.app (Easiest)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```
- Auto-detects Dockerfile
- Free PostgreSQL add-on
- Auto SSL
- ~$5-20/month

### Render.com
1. Connect GitHub repo
2. Select "Web Service"
3. It auto-detects Dockerfile
4. Add PostgreSQL database
5. Done!

### DigitalOcean App Platform
1. Connect GitHub
2. Select repo
3. Configure as Docker app
4. Add managed database
5. Deploy

---

## My Honest Recommendation

For your first deployment:

1. **Start with Railway or Render** - Get live in 30 minutes, not 3 days
2. **Focus on the app** - Make sure it works well for users
3. **Migrate to AWS later** - When you need more control or cost savings

AWS is powerful but complex. Learning it while also launching an app is a lot. The simpler platforms handle SSL, databases, deployments, and scaling automatically.

Once you have users and understand your needs better, migrating to AWS will be much easier because you'll know exactly what you need.

---

## Questions to Ask Yourself

Before deploying anywhere:

1. **How many users do you expect?**
   - <100: SQLite is fine, simplest platform wins
   - 100-1000: Need PostgreSQL, any platform works
   - 1000+: Need AWS or similar for scaling

2. **How critical is uptime?**
   - Side project: Single server is fine
   - Business critical: Need redundancy (more complex)

3. **Budget?**
   - <$20/mo: Railway, Render, or minimal AWS
   - $20-50/mo: Comfortable AWS setup
   - $50+/mo: Production-ready with backups and monitoring

4. **How much time to maintain?**
   - Minimal: Managed platforms (Railway, Render)
   - Some time: AWS with automation
   - Lots of time: Custom AWS setup
