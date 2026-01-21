# Golf Fantasy League

A full-stack fantasy golf application where users create private leagues, draft PGA Tour golfers, and compete based on real tournament scores.

## 🏗️ Architecture

- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS
- **Backend**: FastAPI + Python 3.11+ + PostgreSQL
- **API**: Live Golf Data (RapidAPI)
- **Deployment**: Vercel (frontend) + DigitalOcean (backend)

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL (via Docker)

### Backend Setup
```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### Environment Setup
Create `.env` in `backend/` directory:
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/golf_fantasy
SECRET_KEY=your-secret-key-here
GOLF_API_KEY=your-rapidapi-key
GOLF_API_BASE_URL=https://live-golf-data.p.rapidapi.com

# Scheduler Configuration (optional - defaults shown)
ENABLE_AUTO_SYNC=true
SYNC_INTERVAL_MINUTES=10
TOURNAMENT_IMPORT_WINDOW_DAYS=365
PLAYER_REFRESH_WINDOW_DAYS=7
SCORE_SYNC_PLAYING_HOURS_START=6
SCORE_SYNC_PLAYING_HOURS_END=22
COMPLETED_SYNC_LOOKBACK_DAYS=7
```

**Note**: The scheduler starts automatically when the backend launches. You'll see log messages confirming all 4 jobs are scheduled.

### Database Setup
```bash
# Start PostgreSQL
docker-compose up postgres -d

# Run migrations
cd backend
alembic upgrade head
```

### Start Backend
```bash
cd backend
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## 🎯 Current Status: Production Ready (99%)

**Last Updated**: January 20, 2026

### ✅ Completed Features
- **Authentication System**: 3-tier permissions (User/Admin/Owner)
- **Automated Scheduler**: 4 background jobs for tournament/player/score management
  - Job #1: Daily tournament import (6 AM ET)
  - Job #2: Weekly player refresh (Fridays 6 PM ET)
  - Job #3: Active score sync (every 10 minutes)
  - Job #4: Completed tournament sync (Sundays 10 PM ET)
- **Tournament Management**: Fully automated import and refresh
- **League System**: Create, join via invite codes, standings
- **Team Drafting**: 4-player teams with proper UUID handling
- **Player Display**: Names, round scores (R1-R4), total scores
- **Draft Enforcement**: Team limit properly enforced, buttons disabled when full
- **Score Integration**: Real-time score syncing during tournaments
- **Admin Portal**: User management (automated operations via scheduler)
- **SSR Safety**: All localStorage access properly guarded
- **Smart Round Detection**: Optimized syncing based on tournament status

### 🚨 Known Limitation
**Golf API Player Data Timing** (Handled Automatically): The Live Golf Data API doesn't populate player fields until ~1 week before tournament start. The scheduler automatically handles this by running Job #2 (Player Refresh) every Friday at 6 PM ET, refreshing players for tournaments in the next 7 days. No manual intervention needed.

For local development testing, use past tournaments (Jan-Feb 2025) with complete player data.

**See**: `KNOWN_ISSUES.md` for details.

## 📁 Project Structure

```
golf-pickem-league/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── models/         # SQLAlchemy models
│   │   ├── routes/         # API endpoints
│   │   ├── services/      # Golf API integration
│   │   ├── schemas/       # Pydantic models
│   │   └── utils/         # Auth, dependencies
│   ├── scripts/           # Utility scripts
│   │   ├── import_2025_tournaments.py
│   │   └── sync_completed_scores.py
│   ├── alembic/           # Database migrations
│   └── requirements.txt
├── frontend/               # Next.js frontend
│   ├── app/               # App router pages
│   ├── components/        # React components
│   └── lib/               # API client, auth
├── docker-compose.yml      # PostgreSQL setup
└── .env                   # Environment variables
```

## 🔧 Utility Scripts

**Note**: In production, these operations are fully automated by the scheduler. Scripts are provided for development/testing only.

### Import Tournaments (Automated in Production)
```bash
cd backend
python scripts/import_2025_tournaments.py
```
Imports first 5 and last 5 tournaments from 2025 PGA Tour schedule.

**Production**: Job #1 runs daily at 6 AM ET automatically.

### Sync Scores (Automated in Production)
```bash
cd backend
python scripts/sync_completed_scores.py
```
Syncs round-by-round scores for all completed tournaments from the Golf API.

**Production**: Jobs #3 and #4 handle this automatically:
- Job #3: Active tournaments (every 10 minutes during play hours)
- Job #4: Completed tournaments (Sundays 10 PM ET)

### Manual Player Refresh (If Needed)
```bash
cd backend
python -c "from app.services.tournament_service import refresh_tournament_players; refresh_tournament_players(tournament_id='your-id')"
```

**Production**: Job #2 runs every Friday at 6 PM ET automatically.

## 🧪 Testing

### Backend Testing
```bash
cd backend
# Test API endpoints
curl http://localhost:8000/docs
```

### Frontend Testing
See `FRONTEND_TESTING.md` for comprehensive testing guide.

## 🚀 Production Deployment

**Ready to Deploy!**

See `DEPLOYMENT_GUIDE.md` for comprehensive step-by-step deployment instructions.

**Quick Links**:
- Digital Ocean App Platform setup
- Vercel frontend deployment
- Environment variable configuration
- Database setup and migrations
- Scheduler verification
- Log monitoring instructions

Also see `PRODUCTION_CHECKLIST.md` for deployment checklist.

## 📚 Documentation

- `DEPLOYMENT_GUIDE.md` - **Complete production deployment guide**
- `PRODUCTION_CHECKLIST.md` - Production deployment checklist
- `KNOWN_ISSUES.md` - Current known issues (all resolved)
- `IMPLEMENTATION_PLAN.md` - Original development plan
- `FRONTEND_TESTING.md` - Frontend testing guide

## 🔄 Next Session Resume

See `RESUME_GUIDE.md` for how to pick up development.

## 🧪 Testing In Progress

**Servers Running**:
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- Database: PostgreSQL (Docker)

**Testing Plan**: See `MANUAL_TEST_PLAN.md` and `TESTING_STATUS.md`

## 📞 Support

Check the documentation files for detailed setup and troubleshooting guides.