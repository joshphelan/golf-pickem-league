# App Deployment Strategy Guide

**Last Updated**: January 21, 2026

This guide compares modern deployment options for the Golf Pick'em League app, considering:
- **Hobby-friendly pricing** (start cheap, pay as you grow)
- **Background job support** (APScheduler needs persistent runtime)
- **PostgreSQL database** requirements
- **Scalability path** for future growth

---

## Application Requirements Summary

| Component | Technology | Deployment Needs |
|-----------|------------|------------------|
| Frontend | Next.js 14 + TypeScript | Static/SSR hosting, edge CDN |
| Backend | FastAPI + Python 3.11 | Persistent process for APScheduler |
| Database | PostgreSQL | Managed DB preferred |
| Background Jobs | APScheduler (in-process) | Runs inside backend process |
| External API | RapidAPI Golf Data | Outbound HTTPS calls |

### Critical Requirement: Background Jobs

Your app runs **4 scheduled jobs** via APScheduler:
1. Weekly tournament import
2. Player refresh (16x/week)
3. Live score sync (every 10 minutes)
4. Daily backup sync

**APScheduler runs in-process** with your FastAPI app, which means:
- ✅ Simple deployment (no separate worker needed)
- ⚠️ Requires **persistent process** (not serverless/Lambda)
- ⚠️ Single instance only (multiple replicas = duplicate jobs)

---

## Deployment Options Comparison

### Option 1: Vercel + DigitalOcean (Current Recommendation)

**Architecture:**
```
┌─────────────────────┐     ┌──────────────────────────────┐
│   Vercel (Free)     │────▶│  DigitalOcean App Platform   │
│   Next.js Frontend  │     │  FastAPI + APScheduler       │
└─────────────────────┘     └──────────────┬───────────────┘
                                           │
                            ┌──────────────▼───────────────┐
                            │  DigitalOcean Managed        │
                            │  PostgreSQL                  │
                            └──────────────────────────────┘
```

**Pros:**
- ✅ Vercel has best-in-class Next.js support (automatic optimizations)
- ✅ Free Vercel tier is generous (100GB bandwidth)
- ✅ DO App Platform handles Docker/deployments automatically
- ✅ Managed PostgreSQL with automatic backups
- ✅ Easy to scale independently (frontend vs backend)
- ✅ GitHub auto-deploy on push

**Cons:**
- ❌ Two platforms to manage
- ❌ DO managed PostgreSQL starts at $15/month
- ❌ Slightly more complex initial setup

**Monthly Cost:**
| Tier | Frontend | Backend | Database | Total |
|------|----------|---------|----------|-------|
| Testing | Vercel Free | DO Basic $5 | DO Dev DB $0 | **$5/mo** |
| Production | Vercel Free | DO Professional $12 | DO PostgreSQL $15 | **$27/mo** |
| Scaled | Vercel Pro $20 | DO Pro+ $24 | DO PostgreSQL Pro $60 | **$104/mo** |

---

### Option 2: Railway (All-in-One)

**Architecture:**
```
┌───────────────────────────────────────┐
│              Railway                   │
│  ┌─────────────┐  ┌─────────────────┐ │
│  │  Next.js    │  │    FastAPI      │ │
│  │  Frontend   │  │  + APScheduler  │ │
│  └─────────────┘  └────────┬────────┘ │
│                            │          │
│  ┌─────────────────────────▼────────┐ │
│  │         PostgreSQL               │ │
│  └──────────────────────────────────┘ │
└───────────────────────────────────────┘
```

**Pros:**
- ✅ **Simplest setup** - one platform for everything
- ✅ **Usage-based pricing** - only pay for what you use
- ✅ Built-in PostgreSQL provisioning (click to add)
- ✅ Excellent developer experience
- ✅ GitHub auto-deploy
- ✅ Good for monorepo structure
- ✅ Cron jobs built-in (alternative to APScheduler)
- ✅ Sleeps when idle (cost savings)

**Cons:**
- ❌ Next.js not as optimized as Vercel (no edge functions)
- ❌ Less mature than Vercel/DO for large scale
- ❌ $5 minimum monthly spend (hobby plan)
- ❌ Can get expensive if backend never sleeps

**Monthly Cost:**
| Tier | Estimate | Notes |
|------|----------|-------|
| Hobby (low traffic) | **$5-15/mo** | Usage-based, services can sleep |
| Active (always-on backend) | **$20-40/mo** | Backend runs 24/7 for scheduler |
| Scaled | **$50-100+/mo** | Higher compute needs |

**⚠️ Important Railway Consideration:**
If your backend sleeps (Railway's cost-saving feature), APScheduler jobs won't run. You need to either:
1. Keep backend always-on (higher cost)
2. Use Railway's native Cron instead of APScheduler (recommended)
3. Accept jobs only run when backend is active

---

### Option 3: Render

**Architecture:** Similar to Railway (all-in-one platform)

**Pros:**
- ✅ Free tier available (with limitations)
- ✅ Simple deployment from GitHub
- ✅ Built-in PostgreSQL
- ✅ Background workers supported
- ✅ Good documentation

**Cons:**
- ❌ Free tier services sleep after 15min inactivity
- ❌ Wake-up time ~30 seconds (bad UX for first request)
- ❌ PostgreSQL free tier expires after 90 days
- ❌ Need paid tier for always-on backend (scheduler)

**Monthly Cost:**
| Tier | Frontend | Backend | Database | Total |
|------|----------|---------|----------|-------|
| Free (Testing) | Free | Free | Free (90 days) | **$0/mo** |
| Starter | $7 | $7 | $7 | **$21/mo** |
| Production | $15 | $25 | $20 | **$60/mo** |

---

### Option 4: Fly.io + Supabase/Neon

**Architecture:**
```
┌─────────────────────┐     ┌──────────────────────────────┐
│   Vercel (Free)     │────▶│         Fly.io               │
│   Next.js Frontend  │     │  FastAPI + APScheduler       │
└─────────────────────┘     └──────────────┬───────────────┘
                                           │
                            ┌──────────────▼───────────────┐
                            │  Supabase / Neon (Free tier) │
                            │  PostgreSQL                  │
                            └──────────────────────────────┘
```

**Pros:**
- ✅ **Very cheap** - Fly.io has generous free tier
- ✅ Supabase/Neon free PostgreSQL tiers
- ✅ Global edge deployment possible
- ✅ Docker-based (full control)
- ✅ Machines can auto-stop/start

**Cons:**
- ❌ More complex setup (Docker, fly.toml)
- ❌ Need to manage auto-stop carefully for scheduler
- ❌ Free database tiers have limitations
- ❌ Steeper learning curve

**Monthly Cost:**
| Tier | Frontend | Backend | Database | Total |
|------|----------|---------|----------|-------|
| Minimal | Vercel Free | Fly.io Free | Neon Free | **$0/mo** |
| Hobby | Vercel Free | Fly.io ~$5 | Supabase Free | **~$5/mo** |
| Production | Vercel Free | Fly.io ~$15 | Supabase Pro $25 | **~$40/mo** |

---

### Option 5: Self-Hosted (DigitalOcean Droplet)

**Architecture:**
```
┌─────────────────────┐     ┌──────────────────────────────┐
│   Vercel (Free)     │────▶│     DO Droplet ($6/mo)       │
│   Next.js Frontend  │     │  ┌────────────────────────┐  │
└─────────────────────┘     │  │ Docker Compose         │  │
                            │  │ - FastAPI              │  │
                            │  │ - PostgreSQL           │  │
                            │  │ - Nginx (optional)     │  │
                            │  └────────────────────────┘  │
                            └──────────────────────────────┘
```

**Pros:**
- ✅ **Cheapest all-in option** ($6/mo for everything)
- ✅ Full control over environment
- ✅ No service sleep issues
- ✅ PostgreSQL runs locally (no network latency)
- ✅ Easy to add Redis, etc. later

**Cons:**
- ❌ **You manage everything** (updates, security, backups)
- ❌ No auto-scaling
- ❌ Need to set up SSL, firewall, etc.
- ❌ Single point of failure
- ❌ Manual deployment (or set up CI/CD yourself)

**Monthly Cost:**
| Tier | Droplet | Total |
|------|---------|-------|
| Minimal | $6 (1GB RAM) | **$6/mo** |
| Recommended | $12 (2GB RAM) | **$12/mo** |
| Comfortable | $24 (4GB RAM) | **$24/mo** |

---

## Recommendation Matrix

| Scenario | Recommended Option | Why |
|----------|-------------------|-----|
| **Just starting, want simplest setup** | Railway | One platform, usage-based, great DX |
| **Production-ready, best performance** | Vercel + DO | Best-in-class for each component |
| **Cheapest possible** | Fly.io + Neon/Supabase | Free tiers stack up |
| **Full control, don't mind ops work** | DO Droplet | $6-12/mo for everything |
| **Team of developers** | Vercel + DO | Better for collaboration |

---

## My Recommendation for Your App

Given your requirements (hobby app that could scale, background jobs), I recommend:

### Start: Railway (Simplest Path)

**Why Railway for starting out:**
1. **Single platform** - no context switching
2. **Usage-based** - costs scale with actual usage
3. **Quick setup** - deploy in minutes
4. **Good enough** - for hobby/MVP stage

**Setup steps:**
1. Create Railway account
2. Connect GitHub repo
3. Add PostgreSQL database (one click)
4. Deploy frontend service (root: `/frontend`)
5. Deploy backend service (root: `/backend`)
6. Set environment variables
7. Done!

**Cost estimate:** $15-30/month depending on traffic

### Scale: Migrate to Vercel + DigitalOcean

**When to migrate:**
- Frontend needs edge optimizations
- Backend needs more than 8GB RAM
- You want separate scaling for each component
- You need production SLAs

**Migration is straightforward** because:
- Your Docker setup already works
- Environment variables are the same
- Just pointing to different URLs

---

## Background Job Considerations

### Option A: Keep APScheduler (Current)

Works with any persistent hosting (Railway, DO, Render paid tier, Droplet).

**Pros:** Simple, already implemented
**Cons:** Single instance only, jobs lost if process restarts

### Option B: Migrate to External Scheduler

If you want more reliability, consider:

1. **Railway Cron Jobs** - Built into Railway, runs on schedule
2. **GitHub Actions Scheduled Workflows** - Free, triggers your API endpoints
3. **Celery + Redis** - Industry standard, but more complex

**GitHub Actions example** (free, reliable):
```yaml
# .github/workflows/sync-scores.yml
name: Sync Golf Scores
on:
  schedule:
    - cron: '*/10 6-22 * * *'  # Every 10 min, 6am-10pm UTC
jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - run: curl -X POST ${{ secrets.API_URL }}/api/internal/sync-scores
```

This approach:
- ✅ Works even if backend sleeps
- ✅ Free (GitHub Actions minutes)
- ✅ Survives restarts/deployments
- ❌ Requires adding internal API endpoints

---

## Quick Start: Railway Deployment

Here's how to deploy to Railway today:

### 1. Create Railway Account
Go to [railway.app](https://railway.app) and sign up with GitHub.

### 2. Create New Project
Click "New Project" → "Deploy from GitHub repo"

### 3. Add PostgreSQL
In your project, click "+ New" → "Database" → "PostgreSQL"

### 4. Deploy Backend
- Click "+ New" → "GitHub Repo" → Select your repo
- Set root directory: `backend`
- Add environment variables:
  ```
  DATABASE_URL=${{Postgres.DATABASE_URL}}
  SECRET_KEY=<generate-random-64-char>
  GOLF_API_KEY=<your-rapidapi-key>
  GOLF_API_BASE_URL=https://live-golf-data.p.rapidapi.com
  ENABLE_AUTO_SYNC=true
  SYNC_INTERVAL_MINUTES=10
  CORS_ORIGINS=https://your-frontend.up.railway.app
  ```

### 5. Deploy Frontend
- Click "+ New" → "GitHub Repo" → Select your repo
- Set root directory: `frontend`
- Add environment variable:
  ```
  NEXT_PUBLIC_API_URL=https://your-backend.up.railway.app
  ```

### 6. Generate Domains
Click on each service → Settings → Generate Domain

---

## Migration Path Summary

```
Phase 1 (Now): Railway - Simple, affordable, works great
     │
     ▼ (When you need more)
Phase 2: Vercel (frontend) + Railway (backend + DB)
     │
     ▼ (When you need production-grade)
Phase 3: Vercel + DO App Platform + DO Managed PostgreSQL
     │
     ▼ (When you need enterprise)
Phase 4: Kubernetes / AWS ECS / etc.
```

You likely won't need Phase 3+ for a fantasy golf league, but the path is there.

---

## Cost Comparison Summary

| Platform | Minimal | Hobby Active | Production |
|----------|---------|--------------|------------|
| **Railway** | $5/mo | $20-30/mo | $50-80/mo |
| **Vercel + DO** | $5/mo | $27/mo | $60-100/mo |
| **Render** | $0* | $21/mo | $60/mo |
| **Fly.io + Neon** | $0* | $5-10/mo | $40/mo |
| **DO Droplet** | $6/mo | $12/mo | $24/mo |

*Free tiers have significant limitations (sleep, expiring DBs)

---

## Final Recommendation

**For your Golf Fantasy League hobby app:**

### Go with Railway to start

1. Simplest deployment experience
2. PostgreSQL included
3. Usage-based pricing ($15-30/mo)
4. Background jobs work (keep backend warm)
5. Easy to migrate later if needed

### Keep your existing DEPLOYMENT_GUIDE.md

It's well-written and provides a great option for when/if you want to optimize with Vercel + DigitalOcean later.

### Consider GitHub Actions for Jobs

If you find Railway's "always-on" costs too high, migrate scheduled tasks to GitHub Actions calling your API endpoints. This is free and more reliable than in-process schedulers.

---

## Resources

- [Railway Documentation](https://docs.railway.app/)
- [Vercel Documentation](https://vercel.com/docs)
- [DigitalOcean App Platform](https://docs.digitalocean.com/products/app-platform/)
- [Fly.io Documentation](https://fly.io/docs/)
- [Render Documentation](https://render.com/docs)
