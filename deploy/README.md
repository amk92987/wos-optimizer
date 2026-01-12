# Bear's Den - AWS Deployment Guide

## Architecture

```
[Users] --> [Nginx (port 80/443)] --> [Streamlit App (port 8501)]
                  |
                  +--> /login    --> /?page=login
                  +--> /register --> /?page=register
                  +--> /signup   --> /?page=register
```

Nginx acts as a reverse proxy that:
1. Handles SSL termination (HTTPS)
2. Rewrites clean URLs to query parameters (if someone types /login directly)
3. Proxies WebSocket connections for Streamlit

## Local Development

Works without nginx - just run Streamlit directly:

```bash
streamlit run app.py
```

Access at: http://localhost:8501

The app uses query parameters (`?page=login`) internally, which work both locally and in production.

## Production Deployment (Docker)

```bash
cd deploy
docker-compose up -d
```

Access at: http://localhost (port 80)

## AWS Deployment Options

### Option 1: EC2 with Docker (Recommended)

1. **Launch EC2 instance**
   - AMI: Amazon Linux 2023 or Ubuntu 22.04
   - Instance type: t3.small or larger
   - Security group: Allow ports 22 (SSH), 80 (HTTP), 443 (HTTPS)

2. **Install Docker and Docker Compose**
   ```bash
   # Amazon Linux 2023
   sudo yum install -y docker
   sudo systemctl start docker
   sudo systemctl enable docker
   sudo usermod -aG docker ec2-user

   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose

   # Log out and back in for group changes
   exit
   ```

3. **Clone and deploy**
   ```bash
   git clone <your-repo-url> WoS
   cd WoS/deploy
   docker-compose up -d
   ```

4. **Verify deployment**
   ```bash
   docker-compose ps
   curl http://localhost/healthz
   ```

### Option 2: AWS ECS (Elastic Container Service)

1. **Create ECR repositories**
   ```bash
   aws ecr create-repository --repository-name bearsden-app
   aws ecr create-repository --repository-name bearsden-nginx
   ```

2. **Build and push images**
   ```bash
   # Login to ECR
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

   # Build and push app
   docker build -t bearsden-app -f deploy/Dockerfile .
   docker tag bearsden-app:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/bearsden-app:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/bearsden-app:latest
   ```

3. **Create ECS cluster, task definition, and service via AWS Console or CloudFormation**

### Option 3: AWS App Runner

Simpler but less control:

1. Push code to GitHub/CodeCommit
2. Create App Runner service from source
3. Configure build settings to use Dockerfile

## SSL/HTTPS Setup

### Option A: Let's Encrypt (Free)

```bash
# Install certbot on EC2
sudo yum install -y certbot  # Amazon Linux
# or
sudo apt install -y certbot  # Ubuntu

# Stop nginx temporarily
docker-compose stop nginx

# Get certificate
sudo certbot certonly --standalone -d www.randomchaoslabs.com -d randomchaoslabs.com

# Copy certificates
sudo cp /etc/letsencrypt/live/www.randomchaoslabs.com/fullchain.pem deploy/ssl/
sudo cp /etc/letsencrypt/live/www.randomchaoslabs.com/privkey.pem deploy/ssl/
sudo chown $USER:$USER deploy/ssl/*.pem

# Update docker-compose to use nginx-ssl.conf
# Edit docker-compose.yml: change nginx.conf to nginx-ssl.conf

# Restart
docker-compose up -d
```

**Auto-renewal cron job:**
```bash
echo "0 0 1 * * certbot renew --quiet && cp /etc/letsencrypt/live/www.randomchaoslabs.com/*.pem /path/to/deploy/ssl/ && docker-compose -f /path/to/deploy/docker-compose.yml restart nginx" | sudo tee -a /etc/crontab
```

### Option B: AWS Certificate Manager + ALB

1. Request certificate in ACM for www.randomchaoslabs.com
2. Create Application Load Balancer
3. Add HTTPS listener with ACM certificate
4. Forward to EC2 target group on port 80

## DNS Setup (Route 53)

1. Create hosted zone for randomchaoslabs.com
2. Add A record pointing to EC2 Elastic IP or ALB DNS name
3. Add CNAME for www → root domain (or another A record)

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| STREAMLIT_SERVER_PORT | App port | 8501 |
| STREAMLIT_SERVER_HEADLESS | Run without browser | true |

## Database Persistence

The SQLite database is stored in `/app/data/`. The docker-compose.yml mounts this as a volume to persist data across container restarts.

For production, consider migrating to PostgreSQL or MySQL on AWS RDS.

## Monitoring & Logs

```bash
# View logs
docker-compose logs -f

# View app logs only
docker-compose logs -f app

# View nginx logs only
docker-compose logs -f nginx
```

## Health Checks

| Endpoint | Service | Expected Response |
|----------|---------|-------------------|
| /healthz | Nginx | 200 OK |
| /_stcore/health | Streamlit | 200 OK |

## Updating the Application

```bash
cd WoS
git pull origin main
cd deploy
docker-compose build app
docker-compose up -d
```

## Troubleshooting

### WebSocket connection fails
- Ensure security group allows inbound on port 80/443
- Check nginx logs: `docker-compose logs nginx`

### App not responding
- Check app logs: `docker-compose logs app`
- Verify container is running: `docker-compose ps`

### CSS/JS not loading
- Clear browser cache
- Check nginx is proxying all paths correctly

### Database issues
- Check volume mount: `docker volume ls`
- Backup data: `docker cp bearsden-app:/app/data ./backup`

### SSL certificate issues
- Verify certificate files exist in deploy/ssl/
- Check certificate expiration: `openssl x509 -enddate -noout -in deploy/ssl/fullchain.pem`

## Security Checklist

- [ ] Change default admin password (admin/admin123)
- [ ] Enable HTTPS with valid SSL certificate
- [ ] Configure firewall/security group (only 80, 443)
- [ ] Set up regular database backups
- [ ] Enable CloudWatch logging (optional)
- [ ] Configure rate limiting in nginx (optional)

## Files Reference

| File | Purpose |
|------|---------|
| nginx.conf | HTTP config (development) |
| nginx-ssl.conf | HTTPS config (production) |
| Dockerfile | Streamlit app container |
| docker-compose.yml | Multi-container orchestration |
