# Production Deployment Guide

**Last Updated**: January 20, 2026

This guide provides step-by-step instructions for deploying the Golf Pick'em League application to production using Digital Ocean (backend) and Vercel (frontend).

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Digital Ocean Backend Setup](#digital-ocean-backend-setup)
3. [Vercel Frontend Deployment](#vercel-frontend-deployment)
4. [Environment Variables](#environment-variables)
5. [Monitoring Logs](#monitoring-logs)
6. [Git Workflow](#git-workflow)
7. [Initial Deployment Timeline](#initial-deployment-timeline)
8. [Post-Deployment Verification](#post-deployment-verification)
9. [Troubleshooting](#troubleshooting-common-issues)
10. [Cost Breakdown](#cost-breakdown)

---

## Prerequisites

Before deploying, ensure you have:

- **Digital Ocean account** - Sign up at https://digitalocean.com
- **Vercel account** - Sign up at https://vercel.com
- **GitHub repository** - Your code pushed to GitHub
- **RapidAPI Golf API key** - Subscribe at https://rapidapi.com/apidojo/api/live-golf-data
- **Domain name** (optional) - For custom URLs
- **PostgreSQL knowledge** - Basic understanding of database management

---

## Digital Ocean Backend Setup

We'll use **App Platform** (not Droplets) for easier deployment and automatic scaling.

### Step 1: Create New App

1. Log in to Digital Ocean
2. Click **"Create" → "Apps"**
3. Select **"GitHub"** as source
4. Authorize Digital Ocean to access your repository
5. Select your repository and the **main** branch
6. Click **"Next"**

### Step 2: Configure App Settings

**App Type**: Web Service

**Build Settings**:
- **Source Directory**: `/backend`
- **Build Command**: `pip install -r requirements.txt`
- **Run Command**: `uvicorn app.main:app --host 0.0.0.0 --port 8080`
- **HTTP Port**: `8080`

**Resource Size**:
- Start with **Basic** ($5/month)
- Upgrade if needed based on traffic

### Step 3: Add Database

**Option A: Digital Ocean Managed PostgreSQL** (Recommended)
1. In App Platform, click **"Create" → "Database"**
2. Select **PostgreSQL**
3. Choose **Basic** plan ($15/month)
4. Database will auto-populate `${db.DATABASE_URL}` variable

**Option B: App Platform Dev Database** (Testing Only)
1. Click **"Add Database"**
2. Select **"Dev Database"** (Free, but not for production)
3. Limited performance and reliability

### Step 4: Configure Environment Variables

Go to **Settings → Environment Variables** and add:

```
DATABASE_URL=${db.DATABASE_URL}
SECRET_KEY=<generate-random-64-char-string>
GOLF_API_KEY=<your-rapidapi-key>
GOLF_API_BASE_URL=https://live-golf-data.p.rapidapi.com
ENABLE_AUTO_SYNC=true
SYNC_INTERVAL_MINUTES=10
TOURNAMENT_IMPORT_WINDOW_DAYS=365
PLAYER_REFRESH_WINDOW_DAYS=7
SCORE_SYNC_PLAYING_HOURS_START=6
SCORE_SYNC_PLAYING_HOURS_END=22
COMPLETED_SYNC_LOOKBACK_DAYS=7
CORS_ORIGINS=https://your-frontend.vercel.app
PRIMARY_OWNER_EMAIL=your@email.com
```

**Generate SECRET_KEY**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

### Step 5: Configure Database Migrations

**Option A: Run Manually After First Deploy**
```bash
# SSH into app console (Digital Ocean UI)
python -m app.database init
```

**Option B: Add to Build Script** (Advanced)
Create `backend/run.sh`:
```bash
#!/bin/bash
python -m app.database init
uvicorn app.main:app --host 0.0.0.0 --port 8080
```
Update Run Command to: `bash run.sh`

### Step 6: Configure Health Checks

Digital Ocean automatically configures health checks for `/health` endpoint.

**Default Settings**:
- Path: `/health`
- Interval: 30 seconds
- Timeout: 5 seconds
- Unhealthy threshold: 3 failures

### Step 7: Deploy

1. Review all settings
2. Click **"Create Resources"**
3. Wait 5-7 minutes for initial deployment
4. App will be available at `https://your-app-name.ondigitalocean.app`

---

## Vercel Frontend Deployment

### Step 1: Import Project

1. Log in to Vercel
2. Click **"Add New" → "Project"**
3. Import your GitHub repository
4. Select the repository

### Step 2: Configure Build Settings

**Framework Preset**: Next.js

**Build Settings**:
- **Root Directory**: `frontend`
- **Build Command**: `npm run build` (auto-detected)
- **Output Directory**: `.next` (auto-detected)
- **Install Command**: `npm install` (auto-detected)

### Step 3: Configure Environment Variables

Add in **Settings → Environment Variables**:

```
NEXT_PUBLIC_API_URL=https://your-backend.ondigitalocean.app
```

Replace `your-backend` with your actual Digital Ocean app URL.

### Step 4: Deploy

1. Click **"Deploy"**
2. Wait 2-3 minutes for build
3. App will be available at `https://your-project.vercel.app`

### Step 5: Update Backend CORS (IMPORTANT)

Go back to Digital Ocean and update `CORS_ORIGINS`:
```
CORS_ORIGINS=https://your-project.vercel.app
```

### Step 6: Custom Domain (Optional)

1. In Vercel, go to **Settings → Domains**
2. Add your domain
3. Configure DNS records as instructed
4. Update `CORS_ORIGINS` in Digital Ocean to include custom domain

---

## Environment Variables

### Backend Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | - | PostgreSQL connection string |
| `SECRET_KEY` | Yes | - | 64-character random string for JWT tokens |
| `GOLF_API_KEY` | Yes | - | RapidAPI key for Live Golf Data API |
| `GOLF_API_BASE_URL` | Yes | - | `https://live-golf-data.p.rapidapi.com` |
| `ENABLE_AUTO_SYNC` | No | `true` | Enable background scheduler jobs |
| `SYNC_INTERVAL_MINUTES` | No | `10` | Frequency of score sync checks (Job #3) |
| `TOURNAMENT_IMPORT_WINDOW_DAYS` | No | `365` | How far back to import tournaments (Job #1) |
| `PLAYER_REFRESH_WINDOW_DAYS` | No | `7` | Refresh players for tournaments in next N days (Job #2) |
| `SCORE_SYNC_PLAYING_HOURS_START` | No | `6` | Start hour (ET) for active score syncing |
| `SCORE_SYNC_PLAYING_HOURS_END` | No | `22` | End hour (ET) for active score syncing |
| `COMPLETED_SYNC_LOOKBACK_DAYS` | No | `7` | Days to keep syncing completed tournaments (Job #4) |
| `CORS_ORIGINS` | No | `*` | Comma-separated list of allowed frontend origins |
| `PRIMARY_OWNER_EMAIL` | No | - | Email of primary owner (becomes admin on signup) |

### Frontend Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | Backend API URL (include https://) |

### Example .env Files

**Backend (.env)**:
```env
DATABASE_URL=postgresql://user:pass@host:5432/dbname
SECRET_KEY=your-64-char-random-string-here
GOLF_API_KEY=your-rapidapi-key-here
GOLF_API_BASE_URL=https://live-golf-data.p.rapidapi.com
ENABLE_AUTO_SYNC=true
SYNC_INTERVAL_MINUTES=10
TOURNAMENT_IMPORT_WINDOW_DAYS=365
PLAYER_REFRESH_WINDOW_DAYS=7
SCORE_SYNC_PLAYING_HOURS_START=6
SCORE_SYNC_PLAYING_HOURS_END=22
COMPLETED_SYNC_LOOKBACK_DAYS=7
CORS_ORIGINS=https://your-frontend.vercel.app
PRIMARY_OWNER_EMAIL=your@email.com
```

**Frontend (.env.local)**:
```env
NEXT_PUBLIC_API_URL=https://your-backend.ondigitalocean.app
```

---

## Monitoring Logs

### Digital Ocean Logs

1. Go to **Digital Ocean → Apps → Your App**
2. Click **"Runtime Logs"** tab
3. Select time range (Last 1 hour, 24 hours, etc.)
4. Use search/filter to find specific logs

### Scheduler Logs

The automated scheduler logs all job executions. Look for these patterns:

**Startup Logs** (when app starts):
```
INFO:     Application startup complete.
[Startup] All 4 background jobs scheduled successfully!
Job #1: Import Tournaments - Daily at 06:00 ET
Job #2: Refresh Players - Fridays at 18:00 ET
Job #3: Sync Active Scores - Every 10 minutes
Job #4: Sync Completed Scores - Sundays at 22:00 ET
```

**Job Execution Logs**:
```
# Job #1 (Daily 6am ET) - Tournament Import
[06:00 ET] Job #1: Checking for new tournaments to import
[06:00 ET] Found 3 new tournaments, importing...
[06:01 ET] Successfully imported: The Masters 2026

# Job #2 (Friday 6pm ET) - Player Refresh
[18:00 ET] Job #2: Refreshing players for upcoming tournaments
[18:00 ET] Refreshing 156 players for Sony Open in Hawaii
[18:02 ET] Player refresh complete

# Job #3 (Every 10 min) - Active Score Sync
[10:20 ET] Job #3: Checking 2 potentially active tournaments
[10:20 ET] Sony Open: Round 2, 45 players active
[10:20 ET] Synced scores for 45 players

# Job #4 (Sunday 10pm ET) - Completed Sync
[22:00 ET] Job #4: Final sync for recently completed tournaments
[22:00 ET] Syncing Sony Open (completed 2 days ago)
```

### Filtering Logs

**Search for specific jobs**:
- Job #1: Search for `"Job #1"` or `"Import Tournaments"`
- Job #2: Search for `"Job #2"` or `"Refresh Players"`
- Job #3: Search for `"Job #3"` or `"Sync Active"`
- Job #4: Search for `"Job #4"` or `"Sync Completed"`

**Search for errors**:
- Search for `"ERROR"` or `"Exception"` or `"Failed"`

### Log Retention

Digital Ocean retains logs for:
- **App Platform Basic**: 7 days
- **App Platform Pro**: 30 days

Export logs if you need longer retention.

---

## Git Workflow

### Current Strategy: Single Branch (main)

For simplicity, we're using a single-branch workflow:

**Deployment Triggers**:
- Digital Ocean: Auto-deploys on push to `main`
- Vercel: Auto-deploys on push to `main`

**Making Changes**:
1. Work locally on your main branch
2. Test thoroughly using local development environment
3. Commit changes: `git commit -m "Description"`
4. Push to GitHub: `git push origin main`
5. Automatic deployment begins (2-5 minutes)
6. Verify changes in production

**Important Notes**:
- Every push to `main` deploys to production immediately
- Test carefully before pushing
- No staging environment (yet)
- Consider creating feature branches for large changes

### Future: Two-Branch Strategy

When you're ready for a staging environment:

**Branch Structure**:
- `main` - Production (stable)
- `develop` - Staging (testing)

**Setup Steps**:
1. Create `develop` branch: `git checkout -b develop`
2. Configure Digital Ocean to deploy `develop` to staging app
3. Configure Vercel to deploy `develop` to preview deployment
4. Work on `develop`, test, then merge to `main` for production

**Workflow**:
```bash
# Work on develop
git checkout develop
# Make changes
git commit -m "New feature"
git push origin develop
# Test on staging

# When ready for production
git checkout main
git merge develop
git push origin main
# Deploys to production
```

---

## Initial Deployment Timeline

Here's what to expect when deploying for the first time:

```
T+0 min:   Push code to GitHub main branch
           |
T+1 min:   Digital Ocean detects push, starts build
           Vercel detects push, starts build
           |
T+3 min:   Backend build complete, starting deployment
           |
T+5 min:   Backend deployed, running migrations
           Backend URL live: https://your-app.ondigitalocean.app
           Scheduler starts up
           |
T+5 min:   Scheduler detects empty database
           Job #1 (Import Tournaments) runs immediately
           |
T+6 min:   Importing ~40 tournaments from API
           Tournament import in progress...
           |
T+8 min:   All tournaments imported successfully
           Database populated with tournaments
           |
T+10 min:  Job #3 (Sync Active Scores) runs first check
           Detects no active tournaments (none in progress yet)
           |
T+12 min:  Frontend build complete on Vercel
           Frontend URL live: https://your-app.vercel.app
           |
T+15 min:  Frontend connected to backend
           Both services fully operational
           |
T+20 min:  Sign up as first user → automatically become PRIMARY OWNER
           Full admin access granted
```

**First Hour After Deployment**:
- Scheduler runs Job #3 every 10 minutes (checking for active scores)
- No player refreshes until Friday 6pm ET (Job #2)
- No new tournament imports until tomorrow 6am ET (Job #1)
- Database contains ~40 tournaments but no player details yet

**First Friday 6pm ET**:
- Job #2 runs for the first time
- Refreshes players for all tournaments in next 7 days
- May take 2-5 minutes depending on number of tournaments

**When Tournament Goes Live**:
- Job #3 detects tournament is active (round in progress)
- Begins syncing scores every 10 minutes
- Continues until all rounds complete

---

## Post-Deployment Verification

Use this checklist to verify your deployment:

### Backend Health Check
- [ ] Visit `https://your-backend.ondigitalocean.app/health`
- [ ] Should return: `{"status": "healthy"}`
- [ ] If not, check Digital Ocean logs for errors

### Frontend Loading
- [ ] Visit `https://your-frontend.vercel.app`
- [ ] Homepage loads without errors
- [ ] Can navigate to Sign Up page
- [ ] Console shows no CORS errors (open browser DevTools)

### User Registration
- [ ] Sign up with email matching `PRIMARY_OWNER_EMAIL`
- [ ] Should be redirected to dashboard
- [ ] Should see admin controls (if primary owner)
- [ ] Can create a league

### Scheduler Verification
- [ ] Check Digital Ocean logs
- [ ] Look for: `"All 4 background jobs scheduled successfully!"`
- [ ] Should see list of all 4 jobs with their schedules
- [ ] If not present, check `ENABLE_AUTO_SYNC` env var

### Tournament Import Check
- [ ] Wait 5-10 minutes after deployment
- [ ] Check logs for Job #1 execution
- [ ] Should see: `"Job #1: Checking for new tournaments"`
- [ ] Verify tournaments appear in frontend (browse tournaments)
- [ ] Should see 30-50 tournaments listed

### Database Connectivity
- [ ] Can create a league
- [ ] Can add/remove picks
- [ ] Changes persist after page reload
- [ ] No database connection errors in logs

### CORS Configuration
- [ ] No CORS errors in browser console
- [ ] Frontend can make API calls successfully
- [ ] Check Network tab in DevTools for API calls

### Environment Variables
- [ ] Backend logs show correct `GOLF_API_BASE_URL`
- [ ] No warnings about missing environment variables
- [ ] Scheduler intervals match your configuration

---

## Troubleshooting Common Issues

### Issue: Database Connection Errors

**Symptoms**:
```
ERROR: could not connect to database
ERROR: FATAL: password authentication failed
```

**Solutions**:
1. Verify `DATABASE_URL` format: `postgresql://user:pass@host:5432/dbname`
2. Check database is running (Digital Ocean Database dashboard)
3. Verify database allows connections from App Platform
4. Try running migrations manually: `python -m app.database init`

### Issue: CORS Errors

**Symptoms**:
```
Access to fetch at 'https://backend...' from origin 'https://frontend...'
has been blocked by CORS policy
```

**Solutions**:
1. Update `CORS_ORIGINS` in Digital Ocean to include your Vercel URL
2. Format: `https://your-app.vercel.app` (no trailing slash)
3. For multiple origins: `https://app1.vercel.app,https://app2.vercel.app`
4. Restart backend app after changing env vars

### Issue: Environment Variables Not Loading

**Symptoms**:
```
WARNING: GOLF_API_KEY not configured
ERROR: 'NoneType' object has no attribute 'get'
```

**Solutions**:
1. Go to Digital Ocean → App → Settings → Environment Variables
2. Verify all required variables are set
3. Click **"Save"** (this triggers restart)
4. Wait 2-3 minutes for app to restart
5. Check logs to confirm variables loaded

### Issue: Scheduler Not Starting

**Symptoms**:
- No "All 4 background jobs scheduled" message in logs
- No Job #3 executions every 10 minutes

**Solutions**:
1. Check `ENABLE_AUTO_SYNC=true` is set
2. Verify no syntax errors in `backend/app/scheduler.py`
3. Check logs for scheduler startup errors
4. Try restarting app (Digital Ocean → Actions → Restart)

### Issue: Build Failures

**Backend Build Failures**:
```
ERROR: Could not find a version that satisfies the requirement...
```
- Check `backend/requirements.txt` for typos
- Verify all package versions are valid
- Try building locally first

**Frontend Build Failures**:
```
ERROR: Module not found
```
- Check `frontend/package.json` dependencies
- Verify root directory is set to `frontend` in Vercel
- Try `npm install && npm run build` locally

### Issue: Migration Failures

**Symptoms**:
```
ERROR: relation "tournaments" does not exist
ERROR: schema "public" already exists
```

**Solutions**:
1. SSH into Digital Ocean app console
2. Run: `python -m app.database init`
3. If errors persist, manually connect to database:
   ```sql
   -- Drop all tables and start fresh
   DROP SCHEMA public CASCADE;
   CREATE SCHEMA public;
   ```
4. Re-run migrations

### Issue: No Tournaments Importing

**Symptoms**:
- Scheduler logs show Job #1 runs but no tournaments imported
- Empty tournaments list in frontend

**Solutions**:
1. Verify `GOLF_API_KEY` is correct
2. Check RapidAPI subscription is active
3. Test API manually:
   ```bash
   curl -X GET "https://live-golf-data.p.rapidapi.com/schedule" \
     -H "x-rapidapi-key: YOUR_KEY"
   ```
4. Check logs for API errors: `Search for "GOLF API"`

### Issue: Slow Performance

**Symptoms**:
- API responses take 5+ seconds
- Frontend feels sluggish

**Solutions**:
1. Upgrade Digital Ocean app to higher tier ($12 or $24/month)
2. Add database indexing (contact developer)
3. Enable caching (future feature)
4. Check database query performance in logs

---

## Cost Breakdown

### Digital Ocean

**App Platform - Web Service**:
- Basic ($5/month): 512 MB RAM, 1 vCPU - Good for testing
- Professional ($12/month): 1 GB RAM, 1 vCPU - Recommended for production
- Pro Plus ($24/month): 2 GB RAM, 2 vCPU - For high traffic

**Managed PostgreSQL**:
- Basic ($15/month): 1 GB RAM, 10 GB storage, 25 connections
- Professional ($60/month): 4 GB RAM, 115 GB storage, 97 connections

**Alternative: App Platform Dev Database** (Not Recommended for Production):
- Free tier available
- Limited performance and reliability
- Good for testing only

**Bandwidth**:
- 1 TB outbound transfer included (more than enough)

### Vercel

**Hobby Plan** (Free):
- Unlimited deployments
- 100 GB bandwidth/month
- Enough for most small-to-medium apps

**Pro Plan** ($20/month):
- Unlimited bandwidth
- Team collaboration features
- Needed only for high traffic or teams

### Domain

**Domain Registration**:
- $10-15/year (Namecheap, Google Domains, etc.)
- Optional - can use free Vercel subdomain

### Total Monthly Cost

**Minimal Setup** (Testing):
- Digital Ocean Basic: $5
- Digital Ocean Dev Database: $0
- Vercel Hobby: $0
- **Total: $5/month**

**Recommended Setup** (Production):
- Digital Ocean Professional: $12
- Digital Ocean PostgreSQL: $15
- Vercel Hobby: $0
- **Total: $27/month**

**High-Traffic Setup**:
- Digital Ocean Pro Plus: $24
- Digital Ocean PostgreSQL Pro: $60
- Vercel Pro: $20
- **Total: $104/month**

---

## Additional Resources

- **Digital Ocean App Platform Docs**: https://docs.digitalocean.com/products/app-platform/
- **Vercel Documentation**: https://vercel.com/docs
- **FastAPI Deployment**: https://fastapi.tiangolo.com/deployment/
- **Next.js Deployment**: https://nextjs.org/docs/deployment

---

## Getting Help

If you encounter issues not covered in this guide:

1. Check Digital Ocean logs first
2. Check Vercel deployment logs
3. Review environment variables
4. Test API endpoints manually with curl/Postman
5. Check database connectivity
6. Review GitHub Issues for known problems

---

**Deployment Guide Complete** - Your app should now be running in production!
