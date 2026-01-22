# Railway Deployment Guide for Golf Pick'em League

This guide walks you through deploying the Golf Pick'em League application to Railway, a unified platform that hosts both the backend (FastAPI) and frontend (Next.js) from a single monorepo.

## Table of Contents
- [Why Railway?](#why-railway)
- [Prerequisites](#prerequisites)
- [Architecture Overview](#architecture-overview)
- [Deployment Steps](#deployment-steps)
- [Environment Variables](#environment-variables)
- [Verification](#verification)
- [Monitoring and Maintenance](#monitoring-and-maintenance)
- [Troubleshooting](#troubleshooting)
- [Cost Management](#cost-management)

---

## Why Railway?

Railway provides several advantages for this project:

### Simplicity
- **Single platform**: Manage both backend and frontend from one dashboard
- **Monorepo support**: Automatically detects and deploys multiple services
- **Unified billing**: One bill instead of managing multiple platforms
- **Fast deploys**: Typically 2-3 minutes for full stack deployment

### APScheduler Compatibility
Railway runs persistent containers 24/7, perfect for the application's 4 background jobs:
- Job #1: Tournament Import (Weekly)
- Job #2: Player Refresh (16x/week)
- Job #3: Score Sync (Every 10 minutes)
- Job #4: Backup Sync (Daily)

Containers don't sleep or restart unless you deploy updates. APScheduler jobs run continuously as designed.

### Cost-Effective
**Expected Monthly Cost: $25-30**
```
Base: $5/month (includes $5 in credits, so net $0)
Backend (FastAPI + APScheduler): ~$12-15/month
Frontend (Next.js): ~$6-7/month
PostgreSQL: ~$10/month
Egress: ~$1-2/month
```

---

## Prerequisites

Before starting deployment, gather:

1. **Railway Account**: Sign up at https://railway.app
2. **GitHub Account**: Connected to your golf-pickem-league repository
3. **RapidAPI Golf API Key**: From https://rapidapi.com/fluis.lacasse/api/live-golf-data
4. **Email**: For primary owner account

---

## Architecture Overview

```
┌─────────────────────────────────────────┐
│         Railway Project                 │
│   (golf-pickem-league monorepo)         │
│                                         │
│  ┌───────────────────────────────────┐  │
│  │  SERVICE 1: Backend               │  │
│  │  • Python 3.11 (FastAPI)          │  │
│  │  • Root: /backend                 │  │
│  │  • Port: 8000                     │  │
│  │  • Memory: 1 GB                   │  │
│  │  • APScheduler running 4 jobs     │  │
│  └───────────────┬───────────────────┘  │
│                  │                      │
│  ┌───────────────▼───────────────────┐  │
│  │  SERVICE 2: Frontend              │  │
│  │  • Node.js 20 (Next.js 15)        │  │
│  │  • Root: /frontend                │  │
│  │  • Port: 3000                     │  │
│  │  • Memory: 512 MB                 │  │
│  └───────────────┬───────────────────┘  │
│                  │                      │
│  ┌───────────────▼───────────────────┐  │
│  │  SERVICE 3: PostgreSQL            │  │
│  │  • Railway Managed PostgreSQL     │  │
│  │  • 1 GB RAM, 10 GB storage        │  │
│  │  • Daily automatic backups        │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

---

## Deployment Steps

### Step 1: Create Railway Account and Connect GitHub (5 minutes)

1. Go to https://railway.app
2. Click "Login" and select "Login with GitHub"
3. Authorize Railway to access your GitHub account
4. In Railway, go to Account Settings → Connected Accounts
5. Verify GitHub connection shows your golf-pickem-league repository

### Step 2: Create New Project (2 minutes)

1. Click "New Project" on Railway dashboard
2. Select "Deploy from GitHub repo"
3. Choose `golf-pickem-league` repository
4. Railway will scan the repository and detect:
   - Python application in `/backend`
   - Node.js application in `/frontend`

**Note**: If Railway doesn't auto-detect both services, you'll manually create them in the next steps.

### Step 3: Add PostgreSQL Database (1 minute)

1. In your Railway project, click "+ New"
2. Select "Database"
3. Choose "Add PostgreSQL"
4. Railway provisions a managed PostgreSQL instance
5. The `DATABASE_URL` is automatically created and will be available to your backend service

### Step 4: Configure Backend Service (5 minutes)

#### Create Backend Service (if not auto-detected)
1. Click "+ New" → "Empty Service"
2. Name it "backend"
3. Connect it to your GitHub repository
4. Set root directory to `/backend`

#### Configure Build Settings
Go to backend service → Settings:

**Build Settings**:
- Root Directory: `/backend`
- Build Command: (leave empty - Railway auto-detects pip install)
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

**Resources**:
- Memory: 1024 MB (1 GB)
- vCPU: 1

**Networking**:
- Port: 8000
- Generate Domain: Enable (this creates a public URL)

#### Set Environment Variables
Go to backend service → Variables, and add:

```env
DATABASE_URL=${{Postgres.DATABASE_URL}}
SECRET_KEY=<generate-secret-key>
GOLF_API_KEY=<your-rapidapi-key>
GOLF_API_BASE_URL=https://live-golf-data.p.rapidapi.com
ENABLE_AUTO_SYNC=true
SYNC_INTERVAL_MINUTES=10
TOURNAMENT_IMPORT_WINDOW_DAYS=365
PLAYER_REFRESH_WINDOW_DAYS=7
SCORE_SYNC_PLAYING_HOURS_START=6
SCORE_SYNC_PLAYING_HOURS_END=22
COMPLETED_SYNC_LOOKBACK_DAYS=7
CORS_ORIGINS=
PRIMARY_OWNER_EMAIL=your@email.com
```

**Generate SECRET_KEY**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

**Note**: Leave `CORS_ORIGINS` empty for now. You'll set it after the frontend is deployed.

### Step 5: Configure Frontend Service (5 minutes)

#### Create Frontend Service (if not auto-detected)
1. Click "+ New" → "Empty Service"
2. Name it "frontend"
3. Connect it to your GitHub repository
4. Set root directory to `/frontend`

#### Configure Build Settings
Go to frontend service → Settings:

**Build Settings**:
- Root Directory: `/frontend`
- Build Command: `npm install && npm run build`
- Start Command: `npm start`

**Resources**:
- Memory: 512 MB
- vCPU: 1

**Networking**:
- Port: 3000
- Generate Domain: Enable (this creates a public URL)

#### Set Environment Variables
Go to frontend service → Variables, and add:

```env
NEXT_PUBLIC_API_URL=<backend-service-url>
```

**Get Backend URL**: Go to backend service → Settings → Networking, copy the generated domain (e.g., `https://backend-production-xxxx.up.railway.app`)

### Step 6: Update Backend CORS_ORIGINS (2 minutes)

Now that the frontend is configured:

1. Go to frontend service → Settings → Networking
2. Copy the frontend domain (e.g., `https://frontend-production-xxxx.up.railway.app`)
3. Go to backend service → Variables
4. Update `CORS_ORIGINS` to the frontend domain (without trailing slash)

### Step 7: Deploy Services (5 minutes)

Railway automatically triggers deployments when you save settings. If not:

1. Go to each service
2. Click "Deploy" or "Redeploy"
3. Watch deployment logs:
   - Backend: Look for "All 4 background jobs scheduled successfully!"
   - Frontend: Look for "ready - started server on 0.0.0.0:3000"

**Deployment typically takes**:
- Backend: ~2 minutes
- Frontend: ~1-2 minutes
- Database: Instant (already provisioned)

### Step 8: Run Database Migrations (3 minutes)

After backend is deployed successfully:

#### Option A: Using Railway Shell (Recommended)
1. Go to backend service
2. Click "Shell" tab (opens a terminal in the container)
3. Run migration command:
   ```bash
   alembic upgrade head
   ```
4. Verify output shows successful migration

#### Option B: Using Local Machine
1. Go to PostgreSQL service → Variables
2. Copy the `DATABASE_URL`
3. On your local machine:
   ```bash
   export DATABASE_URL="<railway-database-url>"
   cd backend
   alembic upgrade head
   ```

### Step 9: Verify Deployment (5 minutes)

Test each component:

#### Backend Health Check
```bash
curl https://your-backend.up.railway.app/health
```
Expected response: `{"status": "healthy"}`

#### Check Backend Logs
1. Go to backend service → Deployments → Latest
2. Click "View Logs"
3. Verify you see:
   ```
   All 4 background jobs scheduled successfully!
   - Tournament Import: Weekly on Monday at 00:00
   - Player Refresh: Every 10.5 hours
   - Score Sync: Every 10 minutes (6 AM - 10 PM ET)
   - Backup Sync: Daily at 2 AM
   ```

#### Frontend Check
1. Open `https://your-frontend.up.railway.app` in browser
2. Verify the application loads without errors
3. Open browser console (F12) and check for CORS errors (should be none)

#### Database Check
1. Go to PostgreSQL service → Data
2. Verify tables exist: `users`, `leagues`, `tournaments`, `players`, etc.

#### Functional Tests
1. Sign up as the first user (should become primary owner)
2. Check that tournaments are imported automatically
3. Create a test league
4. Verify functionality works as expected

---

## Environment Variables

### Backend Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `DATABASE_URL` | Yes | PostgreSQL connection string (auto-populated) | `postgresql://user:pass@host/db` |
| `SECRET_KEY` | Yes | Secret key for JWT tokens (generate with script) | `<64-character-random-string>` |
| `GOLF_API_KEY` | Yes | RapidAPI key for Live Golf Data API | `abc123...` |
| `GOLF_API_BASE_URL` | Yes | Base URL for Golf API | `https://live-golf-data.p.rapidapi.com` |
| `ENABLE_AUTO_SYNC` | Yes | Enable automatic background jobs | `true` |
| `CORS_ORIGINS` | Yes | Frontend URL for CORS | `https://frontend.railway.app` |
| `PRIMARY_OWNER_EMAIL` | No | Email of primary owner | `admin@example.com` |
| `SYNC_INTERVAL_MINUTES` | No | Score sync frequency (default: 10) | `10` |
| `TOURNAMENT_IMPORT_WINDOW_DAYS` | No | Days to import tournaments ahead (default: 365) | `365` |
| `PLAYER_REFRESH_WINDOW_DAYS` | No | Days to refresh players (default: 7) | `7` |
| `SCORE_SYNC_PLAYING_HOURS_START` | No | Start hour for score sync ET (default: 6) | `6` |
| `SCORE_SYNC_PLAYING_HOURS_END` | No | End hour for score sync ET (default: 22) | `22` |
| `COMPLETED_SYNC_LOOKBACK_DAYS` | No | Days to sync completed tournaments (default: 7) | `7` |

### Frontend Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Yes | Backend API URL | `https://backend.railway.app` |

---

## Verification

After deployment, complete this checklist:

### Deployment Checklist

- [ ] Backend health endpoint responds: `GET /health`
- [ ] Frontend loads without errors
- [ ] Backend logs show: "All 4 background jobs scheduled successfully!"
- [ ] Database migrations applied successfully
- [ ] No CORS errors in browser console
- [ ] First user signup creates primary owner
- [ ] Tournaments are imported automatically
- [ ] Score sync job runs every 10 minutes (check logs)
- [ ] Can create leagues successfully
- [ ] Can draft players successfully
- [ ] Scores display correctly

### Railway Dashboard Checklist

- [ ] All services show "Active" status
- [ ] Backend service has public domain configured
- [ ] Frontend service has public domain configured
- [ ] PostgreSQL service is connected to backend
- [ ] Environment variables are set correctly
- [ ] Spending limit configured (recommended: $50/month)
- [ ] Usage alerts enabled ($20, $30, $40)

---

## Monitoring and Maintenance

### View Logs

**Real-time Logs**:
1. Go to service → Deployments → Latest
2. Click "View Logs"
3. Logs stream in real-time

**Filter Logs**:
- Use the search bar to filter by keyword
- Use timestamps to find specific events

**Key Log Messages to Monitor**:
- `All 4 background jobs scheduled successfully!` - APScheduler started
- `Tournament import completed: X tournaments added/updated` - Job #1 running
- `Player refresh completed: X players updated` - Job #2 running
- `Score sync completed: X players updated` - Job #3 running
- `Backup sync completed` - Job #4 running

### Monitor Resource Usage

1. Go to service → Metrics
2. View:
   - CPU usage (should average 10-20% for backend)
   - Memory usage (should stay under 80% of allocated)
   - Network egress (should be low)

**Adjust Resources if Needed**:
- Go to Settings → Resources
- Use sliders to adjust memory/CPU
- Click "Save" to apply (will trigger redeploy)

### Monitor Costs

1. Go to Account → Billing
2. View current month usage in real-time
3. Estimated cost updates daily
4. Review detailed breakdown by service

**Set Spending Limits**:
1. Go to Account → Billing → Spending Limit
2. Set maximum (recommended: $50/month)
3. Enable alerts at $20, $30, $40

### Database Backups

**Automatic Backups**:
- Railway PostgreSQL includes daily automatic backups
- Retention: 7 days on free tier, 14 days on paid plans

**Manual Backup**:
1. Go to PostgreSQL service → Data
2. Click "Create Backup"
3. Backup is stored in Railway's backup system

**Restore from Backup**:
1. Go to PostgreSQL service → Backups
2. Select backup to restore
3. Click "Restore" (creates new database instance)

### Deployments and Rollbacks

**Deploy New Code**:
1. Push changes to GitHub repository
2. Railway automatically detects changes
3. Triggers deployment for affected services
4. Watch deployment logs for success

**Manual Deployment**:
1. Go to service → Deployments
2. Click "Deploy"
3. Select commit to deploy

**Rollback**:
1. Go to service → Deployments
2. Find previous successful deployment
3. Click "Redeploy"
4. Previous version is restored

---

## Troubleshooting

### Backend Not Starting

**Symptom**: Backend service shows "Crashed" status

**Possible Causes**:
1. Missing environment variables
2. Database connection failure
3. Port configuration incorrect

**Solutions**:
```bash
# Check logs for specific error
# Common issues:

# Missing DATABASE_URL
Error: DATABASE_URL not set
→ Solution: Verify PostgreSQL service is connected

# Port binding error
Error: Address already in use
→ Solution: Ensure start command uses --host 0.0.0.0 --port 8000

# Database connection error
Error: could not connect to server
→ Solution: Check DATABASE_URL format and PostgreSQL service status
```

### Frontend Not Loading

**Symptom**: Frontend service starts but returns errors

**Possible Causes**:
1. `NEXT_PUBLIC_API_URL` not set or incorrect
2. Build failed
3. CORS configuration incorrect

**Solutions**:
```bash
# Check logs for build errors
# Common issues:

# API URL not set
Error: NEXT_PUBLIC_API_URL is undefined
→ Solution: Add variable to frontend service

# CORS errors in browser console
Error: CORS policy blocked
→ Solution: Update backend CORS_ORIGINS to include frontend URL

# Build fails
Error: Module not found
→ Solution: Check package.json dependencies, redeploy
```

### APScheduler Jobs Not Running

**Symptom**: Logs show jobs scheduled but not executing

**Possible Causes**:
1. Container restarting frequently
2. Memory issues
3. Job crashes

**Solutions**:
```bash
# Check scheduler initialization logs
# Look for:
INFO:apscheduler.scheduler:All 4 background jobs scheduled successfully!

# If jobs crash:
ERROR:apscheduler.executors.default:Job raised an exception
→ Solution: Check specific error in logs, likely API key or database issue

# If container restarts:
# Check Metrics for memory usage
→ Solution: Increase memory allocation if near limit
```

### Database Migration Errors

**Symptom**: Migration command fails or tables missing

**Possible Causes**:
1. Migration not run
2. Alembic version conflict
3. Database permissions

**Solutions**:
```bash
# Run migration manually in Railway shell:
alembic upgrade head

# If version conflict:
alembic stamp head
alembic upgrade head

# Check current migration version:
alembic current

# View migration history:
alembic history
```

### CORS Errors

**Symptom**: Browser console shows CORS policy errors

**Possible Causes**:
1. `CORS_ORIGINS` not set or incorrect
2. Frontend URL changed
3. Protocol mismatch (http vs https)

**Solutions**:
```bash
# Backend CORS_ORIGINS should match frontend URL exactly:
# Correct:
CORS_ORIGINS=https://frontend-production-xxxx.up.railway.app

# Incorrect (common mistakes):
CORS_ORIGINS=https://frontend-production-xxxx.up.railway.app/  # trailing slash
CORS_ORIGINS=http://frontend-production-xxxx.up.railway.app    # wrong protocol
CORS_ORIGINS=frontend-production-xxxx.up.railway.app           # missing protocol
```

### High Costs

**Symptom**: Usage exceeds expected $25-30/month

**Possible Causes**:
1. Memory allocation too high
2. High network egress
3. Multiple deployments triggering build minutes

**Solutions**:
```bash
# Check Metrics for actual usage
# Reduce memory if underutilized:
# Backend: Try 768 MB instead of 1 GB
# Frontend: Try 256 MB instead of 512 MB

# Check deployment frequency:
# Each deploy uses build minutes
# Consider fewer commits or batch changes

# Review egress:
# High egress may indicate large API responses
# Consider pagination or response optimization
```

---

## Cost Management

### Expected Monthly Costs

**Typical Usage** (~$25-30/month):
```
Backend Service:
  - Compute (1 vCPU): ~$7-10/month
  - Memory (1 GB): ~$5/month

Frontend Service:
  - Compute (1 vCPU): ~$4-5/month
  - Memory (512 MB): ~$2/month

PostgreSQL:
  - Database (1 GB RAM, 10 GB storage): ~$10/month

Egress: ~$1-2/month
Build Minutes: ~$0-1/month (minimal)
```

### Cost Optimization Tips

1. **Right-size Resources**:
   - Monitor actual memory usage after 1 week
   - Reduce allocation if consistently under 60% utilization
   - Backend: 768 MB may be sufficient
   - Frontend: 256 MB may be sufficient

2. **Batch Deployments**:
   - Each deployment uses build minutes
   - Combine related changes into single commits
   - Use feature branches and deploy less frequently during development

3. **Optimize Build Time**:
   - Railway caches dependencies
   - Avoid `npm ci` which clears cache
   - Use `npm install` for faster builds

4. **Monitor Egress**:
   - High egress indicates large responses
   - Consider response pagination
   - Use compression where possible

5. **Use Spending Limits**:
   - Set hard cap at $50/month
   - Enable email alerts
   - Review monthly usage trends

### Railway Pricing Details

- **Free Trial**: $5 in credits per month (covers base fee)
- **Compute**: ~$0.000463/GB-hour
- **Memory**: ~$0.000231/GB-hour
- **Database**: ~$0.000463/GB-hour
- **Egress**: $0.10/GB (after 100 GB included)

**Calculate your costs**: https://railway.app/pricing

---

## Additional Resources

### Official Railway Documentation
- Railway Docs: https://docs.railway.app
- Railway Blog: https://blog.railway.app
- Railway Discord: https://discord.gg/railway

### Project-Specific Documentation
- Main README: `README.md`
- Production Checklist: `PRODUCTION_CHECKLIST.md`
- API Documentation: `BACKEND.md`
- Frontend Documentation: `FRONTEND.md`

### Support
- Railway Support: support@railway.app
- Railway Status: https://status.railway.app

---

## Comparison with Other Platforms

If you're considering alternatives to Railway, here's how other platforms compare:

### Railway vs Vercel + Digital Ocean

| Aspect | Railway | Vercel + Digital Ocean |
|--------|---------|------------------------|
| **Complexity** | Single platform | Two platforms to manage |
| **Cost** | ~$25-30/month | ~$27/month ($12 DO + $15 Vercel) |
| **Deploy Time** | 2-3 minutes | 7+ minutes |
| **APScheduler** | Fully supported | Supported on DO only |
| **Frontend Performance** | Good (single region) | Excellent (global CDN) |
| **Developer Experience** | Excellent | Good |
| **Billing** | Unified | Separate invoices |

**Choose Railway if**: You want simplicity and unified management
**Choose Vercel + DO if**: You need maximum frontend performance globally

### Railway vs Heroku

| Aspect | Railway | Heroku |
|--------|---------|--------|
| **Cost** | ~$25-30/month | ~$50-100/month |
| **Performance** | Modern infrastructure | Older infrastructure |
| **Developer Experience** | Modern UI | Classic CLI-focused |
| **Monorepo Support** | Excellent | Requires buildpacks |
| **Database Backups** | Included | Add-on required |

**Choose Railway**: Better cost, performance, and DX
**Choose Heroku**: If you need enterprise features or have existing Heroku expertise

---

## Migration from Digital Ocean + Vercel

If you're migrating from an existing Digital Ocean + Vercel deployment:

### Step 1: Export Data
```bash
# From Digital Ocean database
pg_dump $DO_DATABASE_URL > backup.sql
```

### Step 2: Deploy to Railway
Follow the deployment steps in this guide

### Step 3: Import Data
```bash
# To Railway database
psql $RAILWAY_DATABASE_URL < backup.sql
```

### Step 4: Update DNS (if using custom domain)
1. Point DNS to Railway domains
2. Add custom domains in Railway dashboard
3. Railway auto-provisions SSL certificates

### Step 5: Verify and Switch
1. Test Railway deployment thoroughly
2. Update any external services pointing to old URLs
3. Decommission Digital Ocean and Vercel once stable

**Downtime**: Can be zero if you test Railway deployment first, then switch DNS

---

## Success Criteria

Your Railway deployment is successful when:

- [ ] Both frontend and backend services are "Active"
- [ ] Application is accessible via Railway URLs
- [ ] All 4 APScheduler jobs are running and logging activity
- [ ] Tournaments are being imported automatically
- [ ] Scores are syncing every 10 minutes during playing hours
- [ ] Users can sign up, create leagues, and draft players
- [ ] No errors in logs during normal operation
- [ ] Monthly costs are within expected $25-30 range
- [ ] Spending limits and alerts are configured

**Congratulations!** Your Golf Pick'em League is now live on Railway.

---

## Next Steps After Deployment

1. **Monitor for 1 Week**:
   - Check logs daily for any errors
   - Verify all background jobs run successfully
   - Monitor resource usage and costs

2. **Optimize if Needed**:
   - Adjust memory allocation based on actual usage
   - Fine-tune sync intervals if desired
   - Review and optimize API calls

3. **Set Up Alerts**:
   - Configure Railway usage alerts
   - Set up error monitoring (consider Sentry)
   - Enable uptime monitoring (consider UptimeRobot)

4. **Add Custom Domain** (optional):
   - Purchase domain (e.g., golfpickem.com)
   - Configure DNS in Railway
   - SSL certificates auto-provisioned

5. **Plan for Scale**:
   - Monitor user growth
   - Prepare to increase resources if needed
   - Consider caching strategies for high traffic

---

**Questions or issues?** Check the Troubleshooting section or open an issue in the GitHub repository.
