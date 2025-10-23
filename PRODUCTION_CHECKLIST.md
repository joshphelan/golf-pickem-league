# Production Deployment Checklist

## Overview
This checklist covers all the changes needed to move from development to production for the Golf Pickem League application.

## Critical Production Changes

### 1. Tournament Import Automation
**Current (Dev)**: Manual tournament import via UI
**Production**: Automated daily tournament import

**Changes Needed**:
- [ ] Set up scheduled job (cron job or cloud scheduler)
- [ ] Import tournaments automatically (daily at 6 AM EST)
- [ ] Remove manual import UI from production
- [ ] Add environment variable: `ENABLE_AUTO_SYNC=true`
- [ ] Configure `SYNC_INTERVAL_MINUTES=15` for score syncing

**Implementation**:
```python
# backend/app/scheduler.py (create new file)
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from .services.golf_api_service import GolfAPIService
from .database import get_db

def import_tournaments_job():
    """Daily job to import upcoming tournaments"""
    # Implementation here

def sync_active_tournaments():
    """Sync scores for active tournaments"""
    # Implementation here

# In main.py
if settings.ENABLE_AUTO_SYNC:
    scheduler = BackgroundScheduler()
    scheduler.add_job(import_tournaments_job, CronTrigger(hour=6, minute=0))
    scheduler.add_job(sync_active_tournaments, 'interval', minutes=15)
    scheduler.start()
```

### 2. Environment Variables
**Production Environment Variables**:
```bash
# Database
DATABASE_URL=postgresql://user:password@host:port/database

# JWT
JWT_SECRET_KEY=your-super-secure-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=43200

# Golf API
GOLF_API_KEY=your-rapidapi-key
GOLF_API_BASE_URL=https://live-golf-data.p.rapidapi.com

# CORS
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Scheduler
ENABLE_AUTO_SYNC=true
SYNC_INTERVAL_MINUTES=15

# Primary Owner
PRIMARY_OWNER_EMAIL=admin@yourdomain.com
```

### 3. Database Configuration
**Production Database Setup**:
- [ ] Use managed PostgreSQL (AWS RDS, DigitalOcean, etc.)
- [ ] Set up database backups
- [ ] Configure connection pooling
- [ ] Run migrations: `alembic upgrade head`
- [ ] Set up database monitoring

### 4. Security Hardening
**Security Changes**:
- [ ] Use HTTPS only (SSL certificates)
- [ ] Set secure CORS origins (no wildcards)
- [ ] Use strong JWT secret key
- [ ] Implement rate limiting
- [ ] Add request logging
- [ ] Set up monitoring/alerting

### 5. Frontend Production Build
**Frontend Changes**:
- [ ] Update `NEXT_PUBLIC_API_URL` to production backend URL
- [ ] Build production bundle: `npm run build`
- [ ] Deploy to Vercel/Netlify
- [ ] Configure custom domain
- [ ] Set up CDN for static assets

### 6. Remove Development Features
**Remove from Production**:
- [ ] Hide "Import Tournament" button (or restrict to owners only)
- [ ] Remove development warning messages
- [ ] Clean up console.log statements
- [ ] Remove test data

### 7. Monitoring & Logging
**Production Monitoring**:
- [ ] Set up application monitoring (Sentry, DataDog, etc.)
- [ ] Configure log aggregation
- [ ] Set up uptime monitoring
- [ ] Add health check endpoints
- [ ] Monitor API usage/limits

### 8. Performance Optimization
**Performance Changes**:
- [ ] Enable database connection pooling
- [ ] Add Redis for caching (optional)
- [ ] Optimize database queries
- [ ] Set up CDN for static assets
- [ ] Configure gzip compression

## Deployment Steps

### Backend Deployment (DigitalOcean)
1. **Create Droplet**:
   - Ubuntu 22.04 LTS
   - 2GB RAM minimum
   - 50GB SSD

2. **Install Dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3.11 python3.11-venv postgresql nginx
   ```

3. **Setup Application**:
   ```bash
   git clone your-repo
   cd golf-pickem-league/backend
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with production values
   ```

5. **Setup Database**:
   ```bash
   sudo -u postgres createdb golf_pickem
   alembic upgrade head
   ```

6. **Setup Nginx**:
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

7. **Setup Systemd Service**:
   ```ini
   [Unit]
   Description=Golf Pickem API
   After=network.target
   
   [Service]
   User=ubuntu
   WorkingDirectory=/home/ubuntu/golf-pickem-league/backend
   Environment=PATH=/home/ubuntu/golf-pickem-league/backend/venv/bin
   ExecStart=/home/ubuntu/golf-pickem-league/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
   
   [Install]
   WantedBy=multi-user.target
   ```

### Frontend Deployment (Vercel)
1. **Connect Repository**:
   - Connect GitHub repo to Vercel
   - Set build directory: `frontend`
   - Set output directory: `.next`

2. **Environment Variables**:
   ```
   NEXT_PUBLIC_API_URL=https://yourdomain.com/api
   ```

3. **Deploy**:
   - Vercel will auto-deploy on git push
   - Configure custom domain

## Testing Production

### Pre-Deployment Testing
- [ ] Test all API endpoints
- [ ] Verify authentication flow
- [ ] Test league creation and joining
- [ ] Test player drafting
- [ ] Verify score syncing
- [ ] Test all user permission levels

### Post-Deployment Testing
- [ ] Verify HTTPS is working
- [ ] Test from different devices/browsers
- [ ] Verify database connections
- [ ] Test scheduled jobs
- [ ] Monitor error logs
- [ ] Verify performance

## Rollback Plan
- [ ] Keep database backups
- [ ] Document current working version
- [ ] Have rollback procedure ready
- [ ] Test rollback process

## Maintenance Tasks
- [ ] Set up automated backups
- [ ] Monitor API usage limits
- [ ] Update dependencies regularly
- [ ] Monitor performance metrics
- [ ] Plan for scaling

## Cost Considerations
- **Backend**: DigitalOcean Droplet (~$12/month)
- **Database**: Managed PostgreSQL (~$15/month)
- **Frontend**: Vercel (Free tier)
- **Domain**: ~$12/year
- **SSL**: Free with Let's Encrypt
- **Total**: ~$30/month

## Success Criteria
✅ **Production Ready** when:
- All features work in production
- Automated tournament import working
- Score syncing working automatically
- All users can access the app
- Performance is acceptable
- Security measures in place
- Monitoring and backups configured

## Notes
- Keep development environment separate
- Document all configuration changes
- Test thoroughly before going live
- Have support plan ready
- Monitor user feedback
