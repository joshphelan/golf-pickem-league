# Golf Fantasy League

Fantasy golf app where users create private leagues, draft PGA Tour golfers, and compete based on real tournament scores.

## Architecture

- **Frontend**: Next.js 15 + TypeScript + Tailwind CSS
- **Backend**: FastAPI + Python 3.11 + PostgreSQL
- **API**: Live Golf Data (RapidAPI)
- **Deployment**: Railway (Dockerized)

## Quick Start (Docker)

```bash
# Start all services with hot reload
docker-compose up --build

# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
# API docs: http://localhost:8000/docs
```

First user to sign up becomes the primary owner with admin access.

### Rebuild After Dependency Changes

```bash
docker-compose up --build
```

Only needed when `package.json` or `requirements.txt` change. Code changes apply automatically via hot reload.

### Reset Database

```bash
docker-compose down -v  # -v removes volumes (data)
docker-compose up --build
```

## Quick Start (Manual)

<details>
<summary>Click to expand manual setup</summary>

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
```

### Database
```bash
docker-compose up postgres -d
cd backend && alembic upgrade head
```

### Run
```bash
# Terminal 1
cd backend && uvicorn app.main:app --reload

# Terminal 2
cd frontend && npm install && npm run dev
```
</details>

## Environment Variables

Create `.env` in project root:

```env
# Required
GOLF_API_KEY=your-rapidapi-key
SECRET_KEY=your-secret-key

# Optional (defaults shown)
POSTGRES_USER=golf_user
POSTGRES_PASSWORD=golf_password
POSTGRES_DB=golf_league_db
```

## Container Architecture

```
docker-compose.yml (Development)
├── postgres      - Database with persistent volume
├── backend       - FastAPI with hot reload (volume mount)
└── frontend      - Next.js with hot reload (volume mount)

docker-compose.prod.yml (Production testing)
├── postgres      - Database
├── backend       - FastAPI (no volume mount, runs Dockerfile CMD)
└── frontend      - Next.js standalone build
```

### Key Files

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Local development with hot reload |
| `docker-compose.prod.yml` | Test production builds locally |
| `backend/Dockerfile` | Backend container (runs migrations on start) |
| `frontend/Dockerfile` | Frontend container (multi-stage, standalone build) |
| `frontend/next.config.ts` | `output: 'standalone'` for optimized Docker builds |

### How It Works

**Development** (`docker-compose up`):
- Source code mounted into containers
- Changes apply immediately (hot reload)
- `command:` overrides Dockerfile CMD

**Production** (Railway or `docker-compose.prod.yml`):
- Code baked into image at build time
- No volume mounts
- Dockerfile CMD runs directly

## Railway Deployment

Railway uses the Dockerfiles directly. Key settings:

| Service | Port | Root Directory |
|---------|------|----------------|
| Backend | 8080 | `/backend` |
| Frontend | 8080 | `/frontend` |

### Environment Variables (Railway)

**Backend:**
```
DATABASE_URL=${{Postgres.DATABASE_URL}}
SECRET_KEY=<generate-with-python>
GOLF_API_KEY=<your-key>
CORS_ORIGINS=https://${{frontend.RAILWAY_PUBLIC_DOMAIN}}
ENABLE_AUTO_SYNC=true
```

**Frontend:**
```
NEXT_PUBLIC_API_URL=https://${{backend.RAILWAY_PUBLIC_DOMAIN}}/api
```

See `DEPLOYMENT_GUIDE.md` for full deployment instructions.

## Background Jobs

The backend runs 4 automated jobs via APScheduler:

| Job | Schedule | Purpose |
|-----|----------|---------|
| Tournament Import | Daily 6 AM ET | Import upcoming tournaments |
| Player Refresh | Fridays 6 PM ET | Refresh player fields for upcoming tournaments |
| Score Sync | Every 10 min (6 AM-10 PM ET) | Sync live scores during play |
| Backup Sync | Sundays 10 PM ET | Sync completed tournaments |

Jobs start automatically when backend launches. Check logs for: `All 4 background jobs scheduled successfully!`

## Project Structure

```
golf-pickem-league/
├── backend/
│   ├── app/
│   │   ├── models/      # SQLAlchemy models
│   │   ├── routes/      # API endpoints
│   │   ├── services/    # Golf API integration
│   │   └── utils/       # Auth, dependencies
│   ├── alembic/         # Database migrations
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app/             # Next.js pages
│   ├── components/      # React components
│   ├── lib/             # API client
│   ├── Dockerfile
│   └── next.config.ts
├── docker-compose.yml
├── docker-compose.prod.yml
└── .env
```

## Documentation

- `DEPLOYMENT_GUIDE.md` - Railway deployment
- `KNOWN_ISSUES.md` - Known limitations
- `backend/API_REFERENCE.md` - API endpoints
