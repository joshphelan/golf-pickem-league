# Golf Fantasy League - Backend

FastAPI backend for the Golf Fantasy League application.

## Setup

### Create Virtual Environment

```bash
cd backend
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment

Create a `.env` file in the **backend** directory:

```env
# Golf API
GOLF_API_KEY=your_rapidapi_key_here
GOLF_API_BASE_URL=https://live-golf-data.p.rapidapi.com

# Database
DATABASE_URL=postgresql://golf_user:golf_password@localhost:5432/golf_league_db

# Security
SECRET_KEY=your_generated_secret_key_here

# Scheduler Configuration (optional - defaults shown)
ENABLE_AUTO_SYNC=true
SYNC_INTERVAL_MINUTES=10
TOURNAMENT_IMPORT_WINDOW_DAYS=365
PLAYER_REFRESH_WINDOW_DAYS=7
SCORE_SYNC_PLAYING_HOURS_START=6
SCORE_SYNC_PLAYING_HOURS_END=22
COMPLETED_SYNC_LOOKBACK_DAYS=7

# CORS (optional)
CORS_ORIGINS=http://localhost:3000

# Primary Owner (optional)
PRIMARY_OWNER_EMAIL=your@email.com
```

**Generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

### Start Database

```bash
# From project root
docker-compose up -d postgres
```

### Run Migrations

```bash
# Make sure you're in backend/ directory with venv activated
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### Start Development Server

```bash
uvicorn app.main:app --reload
```

API available at:
- http://localhost:8000
- http://localhost:8000/docs (interactive documentation)
- http://localhost:8000/redoc

## Database Models

- **User**: User accounts with approval workflow
- **Tournament**: PGA Tour tournaments
- **Player**: PGA Tour golfers
- **PlayerScore**: Tournament scores by round
- **League**: Fantasy leagues
- **Team**: User teams in leagues
- **TeamPlayer**: Player selections for teams

## API Endpoints

**Authentication:**
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info
- `GET /api/auth/admin/users` - List all users (admin)
- `PATCH /api/auth/admin/users/{id}` - Approve/modify users (admin)

More endpoints added in Phase 2.

## Testing

```bash
# Test the API
curl http://localhost:8000/health

# View interactive docs
open http://localhost:8000/docs
```

## First Admin User

After running migrations and signing up, manually set yourself as admin:

```sql
-- Connect to database
psql -U golf_user -d golf_league_db

-- Set first user as admin
UPDATE users SET is_approved = TRUE, is_admin = TRUE WHERE email = 'your@email.com';
```

## Project Structure

```
backend/
β"œβ"€β"€ app/
β"‚   β"œβ"€β"€ main.py              # FastAPI app
β"‚   β"œβ"€β"€ config.py            # Settings
β"‚   β"œβ"€β"€ database.py          # DB connection
β"‚   β"œβ"€β"€ models/              # SQLAlchemy models
β"‚   β"œβ"€β"€ routes/              # API endpoints
β"‚   β"œβ"€β"€ schemas/             # Pydantic models
β"‚   β"œβ"€β"€ services/            # Business logic
β"‚   └── utils/               # Helpers
β"œβ"€β"€ alembic/                 # Migrations
β"œβ"€β"€ requirements.txt
└── Dockerfile
```

## Background Jobs & Scheduler

### Overview
The application uses APScheduler to run 4 automated background jobs that keep tournament, player, and score data synchronized with the Golf API. The scheduler starts automatically when the backend launches.

**Implementation**: See `app/scheduler.py` and `app/utils/score_sync.py`

### API Rate Limits
**Live Golf Data API** (RapidAPI):
- **Limit**: 2,000 requests/month
- **Estimated Usage**: ~400-600 calls/month
- **Headroom**: 1,400+ requests available for testing/manual operations

### Job Schedule

#### Job #1: Tournament Import (Daily at 6:00 AM ET)
```python
def import_tournaments_job():
    """Import new tournaments from PGA schedule"""
```
- **Frequency**: Daily at 6:00 AM ET
- **API Calls**: 1 call to `/schedule` endpoint
- **Monthly Cost**: ~30 calls
- **Purpose**: Automatically discover and import new tournaments
- **Window**: Imports tournaments from past 365 days (configurable via `TOURNAMENT_IMPORT_WINDOW_DAYS`)
- **Idempotent**: Won't duplicate existing tournaments

#### Job #2: Player Refresh (Weekly - Fridays at 6:00 PM ET)
```python
def refresh_players_job():
    """Refresh player rosters for upcoming tournaments"""
```
- **Frequency**: Every Friday at 6:00 PM ET
- **API Calls**: 1 call per upcoming tournament (typically 1-3 tournaments)
- **Monthly Cost**: ~12-16 calls (4 Fridays × 3 tournaments avg)
- **Purpose**: Update player fields as rosters finalize before tournaments
- **Window**: Refreshes tournaments starting in next 7 days (configurable via `PLAYER_REFRESH_WINDOW_DAYS`)
- **Golf API Limitation**: Player data not available until ~1 week before tournament

#### Job #3: Active Score Sync (Every 10 minutes)
```python
def sync_active_scores_job():
    """Sync scores for active tournaments"""
```
- **Frequency**: Every 10 minutes (configurable via `SYNC_INTERVAL_MINUTES`)
- **Schedule**: Only during playing hours (6 AM - 10 PM ET by default)
- **API Calls**: 1 call per active tournament (typically 1-2 tournaments)
- **Monthly Cost**: ~350-450 calls during tournament weeks
  - 6 calls/hour × 16 hours = 96 calls/day
  - 4 tournament days × 1.5 avg tournaments = ~575 calls/month
- **Purpose**: Real-time score updates during active rounds
- **Smart Detection**: Only syncs if tournament is in an active round
- **Playing Hours**: Configurable via `SCORE_SYNC_PLAYING_HOURS_START` and `SCORE_SYNC_PLAYING_HOURS_END`

#### Job #4: Completed Tournament Sync (Sundays at 10:00 PM ET)
```python
def sync_completed_scores_job():
    """Final sync for recently completed tournaments"""
```
- **Frequency**: Weekly on Sundays at 10:00 PM ET
- **API Calls**: 1 call per recently completed tournament (typically 1-2)
- **Monthly Cost**: ~8-16 calls (4 Sundays × 2 tournaments avg)
- **Purpose**: Ensure final scores are captured for completed tournaments
- **Window**: Syncs tournaments completed in last 7 days (configurable via `COMPLETED_SYNC_LOOKBACK_DAYS`)

### Monthly API Usage Breakdown
| Job | Frequency | Calls/Month | Purpose |
|-----|-----------|-------------|---------|
| Job #1: Tournament Import | Daily | ~30 | Import new tournaments |
| Job #2: Player Refresh | Weekly (Fri) | ~12-16 | Update player rosters |
| Job #3: Active Score Sync | Every 10 min* | ~350-450 | Live score updates |
| Job #4: Completed Sync | Weekly (Sun) | ~8-16 | Final score verification |
| **Total** | - | **~400-512** | - |

*During playing hours (6 AM - 10 PM ET) only

### Configuration Options

All scheduler settings have sensible defaults but can be customized via environment variables:

```env
# Enable/disable scheduler (default: true)
ENABLE_AUTO_SYNC=true

# Job #3 frequency in minutes (default: 10)
SYNC_INTERVAL_MINUTES=10

# Job #1 import window in days (default: 365)
TOURNAMENT_IMPORT_WINDOW_DAYS=365

# Job #2 refresh window in days (default: 7)
PLAYER_REFRESH_WINDOW_DAYS=7

# Job #3 playing hours in ET (default: 6-22)
SCORE_SYNC_PLAYING_HOURS_START=6
SCORE_SYNC_PLAYING_HOURS_END=22

# Job #4 lookback window in days (default: 7)
COMPLETED_SYNC_LOOKBACK_DAYS=7
```

### Smart Optimizations

1. **Idempotent Operations**: Won't duplicate tournaments, players, or scores
2. **Time-Based Filtering**: Only processes relevant tournaments (active, upcoming, recently completed)
3. **Smart Round Detection**: Detects active rounds before syncing (see `app/utils/score_sync.py`)
4. **Playing Hours Only**: Job #3 only runs during configured playing hours
5. **Automatic Cleanup**: Jobs skip if no relevant tournaments found
6. **Error Recovery**: Failed jobs log errors but don't crash the scheduler

### Manual Operations
For testing or manual imports:
```bash
# Import specific tournament
POST /api/tournaments/import
{
  "tourn_id": "475",
  "year": 2025
}

# Refresh players for tournament
POST /api/tournaments/{id}/refresh-players

# Sync scores for tournament
POST /api/tournaments/{id}/sync-scores
```

### Scheduler Startup

When the backend starts, you'll see confirmation logs:

```
INFO:     Application startup complete.
[Startup] All 4 background jobs scheduled successfully!
Job #1: Import Tournaments - Daily at 06:00 ET
Job #2: Refresh Players - Fridays at 18:00 ET
Job #3: Sync Active Scores - Every 10 minutes
Job #4: Sync Completed Scores - Sundays at 22:00 ET
```

### Monitoring

**Local Development**:
- Check console logs for job execution
- Look for `"Job #1"`, `"Job #2"`, `"Job #3"`, `"Job #4"` in logs
- Job #3 runs every 10 minutes (you'll see frequent logs)

**Production**:
- Monitor Digital Ocean Runtime Logs
- Filter by job names to track specific operations
- Check for errors: search for "ERROR" or "Failed"

**API Usage**:
- Monitor RapidAPI dashboard for call counts
- Alert if approaching 2,000 monthly limit
- Export logs if needed for debugging

**Troubleshooting**:
- If scheduler doesn't start, check `ENABLE_AUTO_SYNC=true`
- If jobs don't run, check timezone (scheduler uses ET)
- If no tournaments importing, verify `GOLF_API_KEY` is correct

