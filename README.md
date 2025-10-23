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

## 🎯 Current Status: Phase 4 Complete

### ✅ Completed Features
- **Authentication System**: 3-tier permissions (User/Admin/Owner)
- **Tournament Management**: Import, schedule caching, player refresh
- **League System**: Create, join via invite codes, standings
- **Team Drafting**: 4-player teams with real-time scoring
- **Admin Portal**: User management, tournament import
- **Background Scheduler**: Auto-refresh players for upcoming tournaments
- **Production-Ready**: Environment configs, error handling, validation

### 🔧 Recent Fixes Applied
- Fixed async/sync conflicts in scheduler
- Removed auto-refresh from league creation (performance)
- Added manual "Refresh Players" button
- Fixed team ownership field naming
- Added tournament schedule dropdown
- Improved date/time picker UX

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
│   ├── alembic/           # Database migrations
│   └── requirements.txt
├── frontend/               # Next.js frontend
│   ├── app/               # App router pages
│   ├── components/        # React components
│   └── lib/               # API client, auth
├── docker-compose.yml      # PostgreSQL setup
└── .env                   # Environment variables
```

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

## 🐛 Known Issues

- 422 error on tournament schedule endpoint (authentication issue)
- Need to verify JWT token handling in frontend
- Tournament import requires manual API key setup

## 📞 Support

Check the documentation files for detailed setup and troubleshooting guides.