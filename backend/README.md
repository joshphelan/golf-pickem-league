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

Create a `.env` file in the **project root** (not in backend folder):

```env
# Golf API
GOLF_API_KEY=your_actual_api_key_here
GOLF_API_BASE_URL=https://api.freewebapi.com

# Database
DATABASE_URL=postgresql://golf_user:golf_password@localhost:5432/golf_league_db
POSTGRES_USER=golf_user
POSTGRES_PASSWORD=golf_password
POSTGRES_DB=golf_league_db

# JWT Secret (generate with command below)
SECRET_KEY=your_generated_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# Frontend URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
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

## Background Jobs & API Usage

### Overview
The application uses APScheduler to run automated jobs that keep tournament and player data up-to-date.

### API Rate Limits
**Live Golf Data API** (RapidAPI):
- **Limit**: 2,000 requests/month
- **Monthly Usage**: ~378-552 calls/month
- **Headroom**: 1,400+ requests available for testing/manual operations

### Job Schedule

#### 1. Daily Schedule Sync (6:00 AM daily)
```python
def daily_schedule_sync():
    """Import new tournaments from PGA schedule"""
```
- **Frequency**: Once per day
- **API Calls**: 1 call to `/schedule`
- **Monthly Cost**: 30 calls
- **Purpose**: Discover new tournaments added to schedule

#### 2. Player Field Updates (7:00 AM daily)
```python
def update_upcoming_player_fields():
    """Update player rosters for upcoming tournaments"""
```
- **Frequency**: Once per day
- **Targets**: Tournaments starting within 14 days
- **API Calls**: 2-3 calls to `/tournament` (one per upcoming tournament)
- **Monthly Cost**: 60-90 calls
- **Purpose**: Keep player fields current as rosters finalize before tournaments

#### 3. Live Score Sync (Every 5 minutes during tournament hours)
```python
def sync_active_tournament_scores():
    """Update live scores during active tournaments"""
```
- **Frequency**: Every 5 minutes
- **Schedule**: Thursday-Sunday, 8 AM - 8 PM ET only
- **Targets**: Active tournaments only
- **API Calls**: 12 calls/hour × 12 hours = 144 calls per tournament
- **Monthly Cost**: 288-432 calls (2-3 overlapping tournaments)
- **Purpose**: Real-time score updates for active fantasy leagues

### Monthly API Usage Breakdown
| Job | Calls/Day | Monthly Total |
|-----|-----------|---------------|
| Schedule Sync | 1 | 30 |
| Player Updates | 2-3 | 60-90 |
| Score Sync | 10-14* | 288-432 |
| **Total** | **13-18** | **378-552** |

*Only during active tournament days (Thu-Sun)

### Configuration
Set in `.env` file:
```env
ENABLE_AUTO_SYNC=true           # Enable background jobs
SYNC_INTERVAL_MINUTES=5         # Score sync frequency
```

### Smart Optimizations
1. **Idempotent imports** - Won't duplicate tournaments already in DB
2. **Time-based filtering** - Only updates relevant tournaments (14-day window)
3. **Tournament hours only** - Score syncing only when tournaments are active
4. **Status-based logic** - Different update strategies for upcoming/active/completed tournaments

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

### Monitoring
- Check logs for job execution
- Monitor API call counts in RapidAPI dashboard
- Alert if approaching 2K monthly limit

