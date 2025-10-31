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
Create `.env` in project root:
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/golf_fantasy
SECRET_KEY=your-secret-key-here
GOLF_API_KEY=your-rapidapi-key
GOLF_API_BASE_URL=https://live-golf-data.p.rapidapi.com
ENABLE_AUTO_SYNC=true
```

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

## 🎯 Current Status: Core Functionality Complete (95%)

**Last Updated**: October 31, 2024

### ✅ Completed Features
- **Authentication System**: 3-tier permissions (User/Admin/Owner)
- **Tournament Management**: Automated import scripts, score syncing
- **League System**: Create, join via invite codes, standings
- **Team Drafting**: 4-player teams with proper UUID handling
- **Player Display**: Names, round scores (R1-R4), total scores
- **Draft Enforcement**: Team limit properly enforced, buttons disabled when full
- **Score Integration**: Backend fetches and displays player scores from completed tournaments
- **Admin Portal**: User management (tournament import UI removed - will be automated)
- **SSR Safety**: All localStorage access properly guarded

### 🚨 Known Limitation
**Golf API Player Data Timing**: The Live Golf Data API doesn't populate player fields until ~1 week before tournament start. Currently imported tournaments >1 week away have 0 players. Use past tournaments (Jan-Feb 2025) for testing.

**See**: `KNOWN_ISSUES.md` and `RESUME_GUIDE.md` for details.

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

### Import Tournaments
```bash
cd backend
python scripts/import_2025_tournaments.py
```
Imports first 5 and last 5 tournaments from 2025 PGA Tour schedule.

### Sync Scores
```bash
cd backend
python scripts/sync_completed_scores.py
```
Syncs round-by-round scores for all completed tournaments from the Golf API.

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

See `PRODUCTION_CHECKLIST.md` for deployment steps.

## 📚 Documentation

- `IMPLEMENTATION_PLAN.md` - Original development plan
- `FRONTEND_TESTING.md` - Frontend testing guide
- `PRODUCTION_CHECKLIST.md` - Production deployment
- `KNOWN_ISSUES.md` - Current known issues

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