# Railway Deployment Guide

Deploy the Golf Pick'em League to Railway using Dockerfiles.

## Prerequisites

- Railway account (https://railway.app)
- GitHub repo connected to Railway
- RapidAPI Golf API key

## Architecture

```
Railway Project
├── Backend Service    (Dockerfile in /backend)
├── Frontend Service   (Dockerfile in /frontend)
└── PostgreSQL         (Railway managed)
```

Railway auto-detects the Dockerfiles and builds each service.

## Deployment Steps

### 1. Create Railway Project

1. Railway dashboard → New Project → Deploy from GitHub
2. Select your repository
3. Railway detects two services (backend, frontend)

### 2. Add PostgreSQL

1. In project → "+ New" → Database → PostgreSQL
2. `DATABASE_URL` is auto-generated

### 3. Configure Backend

**Settings → Networking:**
- Port: `8080` (Railway sets PORT=8080)
- Generate domain: Enable

**Variables:**
```
DATABASE_URL=${{Postgres.DATABASE_URL}}
SECRET_KEY=<generate-64-char-key>
GOLF_API_KEY=<your-rapidapi-key>
GOLF_API_BASE_URL=https://live-golf-data.p.rapidapi.com
CORS_ORIGINS=https://${{frontend.RAILWAY_PUBLIC_DOMAIN}}
ENABLE_AUTO_SYNC=true
```

Generate SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

### 4. Configure Frontend

**Settings → Networking:**
- Port: `8080`
- Generate domain: Enable

**Variables:**
```
NEXT_PUBLIC_API_URL=https://${{backend.RAILWAY_PUBLIC_DOMAIN}}/api
```

### 5. Deploy

Push to GitHub. Railway auto-deploys.

Check build logs show Docker steps like `FROM node:20-alpine AS builder`.

## How Dockerfiles Work on Railway

Railway reads each service's Dockerfile:

**Backend Dockerfile:**
```dockerfile
# Runs migrations automatically, then starts server
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
```

**Frontend Dockerfile:**
```dockerfile
# Multi-stage build: builds Next.js, copies standalone output
CMD ["node", "server.js"]
```

### Port Configuration

Railway sets `PORT=8080` environment variable. Both Dockerfiles respect this:
- Backend: `--port ${PORT:-8000}`
- Frontend: Next.js standalone reads `PORT` automatically

**Important:** In Railway settings, set port to `8080` for both services.

## Verification

### Backend
```bash
curl https://your-backend.up.railway.app/health
# {"status": "healthy"}
```

Check logs for:
```
INFO  [alembic.runtime.migration] Running upgrade
All 4 background jobs scheduled successfully!
Uvicorn running on http://0.0.0.0:8080
```

### Frontend
- Visit https://your-frontend.up.railway.app
- No 502 errors
- Can sign up and log in

## Troubleshooting

### 502 Connection Refused

**Cause:** Port mismatch between app and Railway networking config.

**Fix:** Railway → Service → Settings → Networking → Port = `8080`

### "next start" Error

**Cause:** Railway not using Dockerfile (using Nixpacks instead).

**Fix:** Check Settings → Build → Builder = "Dockerfile"

Or add `railway.toml` to force Dockerfile:
```toml
[build]
builder = "dockerfile"
```

### CORS Errors

**Cause:** `CORS_ORIGINS` missing `https://` or has wrong domain.

**Fix:** Set to exact frontend URL:
```
CORS_ORIGINS=https://your-frontend.up.railway.app
```
No trailing slash.

### Migrations Not Running

**Cause:** Backend not using Dockerfile CMD.

**Check:** Look for `Running upgrade` in deploy logs.

**Fix:** Clear any custom start command in Railway settings.

### Frontend 404

**Cause:** Static files not copied in Docker build.

**Fix:** Ensure `frontend/Dockerfile` has:
```dockerfile
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
```

## Environment Variables Reference

### Backend

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection (auto from Railway) |
| `SECRET_KEY` | Yes | JWT signing key (64+ chars) |
| `GOLF_API_KEY` | Yes | RapidAPI key |
| `CORS_ORIGINS` | Yes | Frontend URL with `https://` |
| `ENABLE_AUTO_SYNC` | Yes | Enable background jobs (`true`) |

### Frontend

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | Backend URL with `/api` suffix |

## Cost

Expected: ~$25-30/month

```
Backend:   ~$12-15
Frontend:  ~$6-7
PostgreSQL: ~$10
```

Set spending limit in Railway → Account → Billing.

## Rollback

Railway → Service → Deployments → Click previous deployment → Redeploy

## Local Production Testing

Test the production build locally before deploying:

```bash
docker-compose -f docker-compose.prod.yml up --build
```

This uses the same Dockerfiles Railway uses, without hot reload.
