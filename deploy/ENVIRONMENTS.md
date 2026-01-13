# Environment Strategy & Data Safety

## Environment Overview

| Environment | Purpose | Database | URL |
|-------------|---------|----------|-----|
| **Local Dev** | Development | SQLite (local) | localhost:8501 |
| **Sandbox** | Testing new features | PostgreSQL (RDS) | sandbox.randomchaoslabs.com |
| **Production** | Live users | PostgreSQL (RDS) | www.randomchaoslabs.com |

### Why Three Environments?

1. **Local Dev** - Fast iteration, no risk to real data
2. **Sandbox** - Test with production-like setup before going live
3. **Production** - Real users, real data, maximum caution

---

## Database Strategy

### Development (Local)
- SQLite file: `wos.db`
- Can delete and recreate freely
- No backups needed

### Sandbox
- PostgreSQL on RDS (db.t3.micro - ~$15/month)
- Separate database: `wos_sandbox`
- Weekly automated backups (7-day retention)
- Can be wiped/reset for testing
- Test migrations here BEFORE production

### Production
- PostgreSQL on RDS (db.t3.small - ~$25/month)
- Database: `wos_production`
- **Daily automated backups** (30-day retention)
- **Point-in-time recovery enabled** (5-minute granularity)
- Manual snapshot before ANY deployment
- Multi-AZ for high availability (optional, ~$50/month)

---

## Data Safety Checklist

### Before ANY Production Deployment

```
[ ] 1. Create manual RDS snapshot
      aws rds create-db-snapshot \
        --db-instance-identifier wos-production \
        --db-snapshot-identifier pre-deploy-$(date +%Y%m%d-%H%M)

[ ] 2. Test deployment on Sandbox first
      - Deploy to sandbox
      - Run smoke tests
      - Verify data integrity

[ ] 3. Review migration scripts
      - Check for DROP/DELETE/ALTER operations
      - Ensure all migrations are reversible
      - Test rollback procedure on sandbox

[ ] 4. Schedule maintenance window
      - Notify users if downtime expected
      - Deploy during low-traffic period (2-4 AM)

[ ] 5. Have rollback plan ready
      - Previous Docker image tagged and available
      - Database restore procedure documented
```

### After Production Deployment

```
[ ] 1. Verify application health
      curl https://www.randomchaoslabs.com/healthz
      curl https://www.randomchaoslabs.com/_stcore/health

[ ] 2. Check database connections
      - Monitor RDS connections in CloudWatch
      - Check application logs for errors

[ ] 3. Spot-check user data
      - Login as test user
      - Verify profile loads correctly
      - Check hero data intact

[ ] 4. Monitor for 30 minutes
      - Watch error rates
      - Check response times
      - Be ready to rollback
```

---

## Database Migrations

### Current Problem
The app uses raw SQL for migrations in `database/db.py`. This is risky because:
- No rollback capability
- No migration history tracking
- Hard to test migrations safely

### Recommended Solution: Alembic

Alembic provides:
- Version-controlled migrations
- Rollback support (`alembic downgrade`)
- Migration history in database
- Safe schema changes

**Setup (TODO before production):**
```bash
pip install alembic
alembic init alembic
```

**Migration workflow:**
```bash
# 1. Create migration
alembic revision --autogenerate -m "Add new column"

# 2. Review generated migration
cat alembic/versions/xxx_add_new_column.py

# 3. Test on sandbox
ENVIRONMENT=sandbox alembic upgrade head

# 4. Apply to production
ENVIRONMENT=production alembic upgrade head
```

### Until Alembic is Set Up

**Safe migration rules:**
1. **NEVER DROP columns** without data migration plan
2. **ADD columns as nullable** first, then populate, then add constraints
3. **Test migrations on sandbox** with copy of production data
4. **Keep backup of database** before any schema change

---

## Deployment Procedures

### Standard Deployment (No Database Changes)

```bash
# 1. Pull latest code
cd /opt/WoS
git pull origin main

# 2. Rebuild and restart
cd deploy
docker-compose build app
docker-compose up -d app

# 3. Verify
docker-compose logs -f app  # Watch for errors
curl http://localhost/_stcore/health
```

### Deployment WITH Database Changes

```bash
# 1. Create pre-deployment snapshot
aws rds create-db-snapshot \
  --db-instance-identifier wos-production \
  --db-snapshot-identifier pre-deploy-$(date +%Y%m%d-%H%M)

# 2. Wait for snapshot to complete
aws rds wait db-snapshot-available \
  --db-snapshot-identifier pre-deploy-$(date +%Y%m%d-%H%M)

# 3. Deploy (migrations run automatically on startup)
cd /opt/WoS
git pull origin main
cd deploy
docker-compose build app
docker-compose up -d app

# 4. Verify migrations completed
docker-compose logs app | grep "Migration:"

# 5. Test application
curl http://localhost/_stcore/health
# Login and verify data
```

### Rollback Procedure

**If deployment fails:**

```bash
# Option 1: Rollback to previous image
docker-compose stop app
docker tag bearsden-app:previous bearsden-app:latest
docker-compose up -d app

# Option 2: Restore from snapshot (data loss to snapshot point)
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier wos-production-restored \
  --db-snapshot-identifier pre-deploy-YYYYMMDD-HHMM

# Update DATABASE_URL to point to restored instance
# Restart application
```

---

## Environment Configuration

### Local Development
```bash
# .env (or no .env, uses defaults)
ENVIRONMENT=development
# DATABASE_URL not set = SQLite
```

### Sandbox
```bash
# .env.sandbox (DO NOT COMMIT)
ENVIRONMENT=sandbox
DATABASE_URL=postgresql://wos_user:password@wos-sandbox.xxx.rds.amazonaws.com:5432/wos_sandbox
DEV_AUTO_LOGIN=false
ANTHROPIC_API_KEY=sk-ant-xxx
SECRET_KEY=sandbox-secret-key
```

### Production
```bash
# .env.production (DO NOT COMMIT - use AWS Secrets Manager)
ENVIRONMENT=production
DATABASE_URL=postgresql://wos_user:password@wos-prod.xxx.rds.amazonaws.com:5432/wos_production
DEV_AUTO_LOGIN=false
ANTHROPIC_API_KEY=sk-ant-xxx
SECRET_KEY=production-secret-key-very-long-random
```

---

## AWS Infrastructure Setup

### RDS Setup (One-time)

```bash
# Create Sandbox database
aws rds create-db-instance \
  --db-instance-identifier wos-sandbox \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username wos_admin \
  --master-user-password <password> \
  --allocated-storage 20 \
  --backup-retention-period 7

# Create Production database
aws rds create-db-instance \
  --db-instance-identifier wos-production \
  --db-instance-class db.t3.small \
  --engine postgres \
  --master-username wos_admin \
  --master-user-password <password> \
  --allocated-storage 50 \
  --backup-retention-period 30 \
  --storage-encrypted \
  --deletion-protection
```

### Backup Schedule

| Environment | Automated Backups | Manual Snapshots | Retention |
|-------------|-------------------|------------------|-----------|
| Sandbox | Daily | Before major tests | 7 days |
| Production | Daily | Before every deploy | 30 days |

### Point-in-Time Recovery (Production)

RDS enables point-in-time recovery by default. Can restore to any point within backup retention period:

```bash
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier wos-production \
  --target-db-instance-identifier wos-production-pit \
  --restore-time 2026-01-12T10:00:00Z
```

---

## Monitoring & Alerts

### CloudWatch Alarms (Production)

Set up alerts for:
- [ ] Database CPU > 80%
- [ ] Database connections > 80% of max
- [ ] Database storage < 20% free
- [ ] Application health check failures
- [ ] Error rate > 5%

### Log Retention

| Log Type | Retention |
|----------|-----------|
| Application logs | 30 days |
| Nginx access logs | 14 days |
| Database logs | 7 days |

---

## Cost Estimates (Monthly)

| Component | Sandbox | Production |
|-----------|---------|------------|
| EC2 (t3.small) | $15 | $15 |
| RDS PostgreSQL | $15 (micro) | $25 (small) |
| RDS Storage | $2 | $5 |
| RDS Backups | $1 | $3 |
| Data Transfer | $2 | $5 |
| **Total** | **~$35** | **~$53** |

*Multi-AZ production adds ~$25/month for high availability*

---

## TODO Before Launch

### Critical (Must Have)
- [ ] Set up RDS instances (sandbox + production)
- [ ] Configure automated backups
- [ ] Test backup/restore procedure
- [ ] Create deployment checklist
- [ ] Set up CloudWatch monitoring

### Important (Should Have)
- [ ] Implement Alembic for migrations
- [ ] Set up CI/CD pipeline (GitHub Actions)
- [ ] Configure AWS Secrets Manager for credentials
- [ ] Enable Multi-AZ for production RDS

### Nice to Have
- [ ] Blue-green deployments
- [ ] Automated rollback on health check failure
- [ ] Database replication for read scaling
