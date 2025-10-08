# Golf Fantasy League

A fantasy golf web application where users create private leagues, draft PGA Tour golfers, and compete based on real tournament scores.

## πŸ"‹ Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Free Golf API key (get it at [FreeWebApi](https://freewebapi.com/sports-apis/golf-api/))

### Setup

1. **Clone and configure**
   ```bash
   git clone <your-repo-url>
   cd golf-pickem-league
   cp .env.example .env
   # Edit .env and add your GOLF_API_KEY
   ```

2. **Start the backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

3. **Start the frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Database setup**
   ```bash
   docker-compose up postgres -d
   cd backend
   alembic upgrade head
   ```

## πŸ—οΈ Architecture

### Tech Stack
- **Frontend**: Next.js 14 with TypeScript and Tailwind CSS
- **Backend**: FastAPI with Python
- **Database**: PostgreSQL
- **API**: [Free Golf API](https://freewebapi.com/sports-apis/golf-api/)
- **Deployment**: Vercel (frontend), DigitalOcean (backend)

### Key Features
- ✨ **Private Leagues** with invite code system
- πŸ† **Manual Draft System** - First-come-first-served player selection
- πŸ"Š **Real-Time Scoring** - Automated score updates from PGA tournaments
- πŸ"ˆ **Live Leaderboards** - See your league standings update in real-time
- πŸ"' **Admin Controls** - User approval and league management

### How It Works
1. Users sign up and get approved by admin
2. Admin creates a league for an upcoming PGA tournament
3. Users join via shareable invite link
4. Each user drafts 4 golfers before the tournament starts
5. Scores automatically sync from the Free Golf API
6. Team score = sum of all 4 golfers' stroke scores (lower wins!)
7. Watch the leaderboard update throughout the tournament

## πŸ"š Documentation

- **[IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md)** - Complete 3-week implementation roadmap
- **[.cursorrules](./.cursorrules)** - AI agent guidelines and project conventions
- **[API Documentation](./docs/API.md)** - Backend API endpoints (to be created)
- **[Database Schema](./docs/DATABASE.md)** - Database design (to be created)

## πŸ"‚ Project Structure

```
golf-pickem-league/
β"œβ"€β"€ backend/               # FastAPI backend
β"‚   β"œβ"€β"€ app/
β"‚   β"‚   β"œβ"€β"€ main.py        # App entry point
β"‚   β"‚   β"œβ"€β"€ models/        # SQLAlchemy models
β"‚   β"‚   β"œβ"€β"€ routes/        # API endpoints
β"‚   β"‚   β"œβ"€β"€ services/      # Business logic
β"‚   β"‚   └── schemas/       # Pydantic models
β"‚   └── alembic/          # DB migrations
β"œβ"€β"€ frontend/             # Next.js frontend
β"‚   β"œβ"€β"€ app/              # App router pages
β"‚   β"œβ"€β"€ components/       # React components
β"‚   └── lib/              # API client & utils
β"œβ"€β"€ docker-compose.yml    # Local development setup
└── .env.example          # Environment variables template
```

## 🎯 Current Status

**Phase**: Pre-Development / Planning Complete

### βœ… Completed
- [x] Project plan finalized
- [x] API provider selected (Free Golf API)
- [x] Repository created
- [x] API key obtained
- [x] Documentation structure set up

### πŸ"„ In Progress
- [ ] Backend foundation (Phase 1)

### πŸ"œ Upcoming
- Phase 1: Backend Foundation & Auth
- Phase 2: Tournament & League Management
- Phase 3: Scoring & Leaderboard
- Phase 4: Frontend Development
- Phase 5: Deployment

See [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md) for detailed roadmap.

## πŸ§ͺ API Testing

The Free Golf API provides:
- World rankings
- Tournament schedules
- Live leaderboards
- Player statistics
- FedExCup standings

Example request:
```bash
curl -H "X-API-Key: YOUR_KEY" \
  "https://api.freewebapi.com/schedules?year=2025&orgId=1"
```

## 🀝 Contributing

This is a personal project, but contributions are welcome!

1. Check the current implementation phase in README
2. Review `.cursorrules` for code conventions
3. Create a feature branch
4. Make your changes
5. Test thoroughly
6. Submit a PR with clear description

## πŸ" Environment Variables

Create a `.env` file in the root directory:

```env
# Free Golf API
GOLF_API_KEY=your_api_key_here
GOLF_API_BASE_URL=https://api.freewebapi.com

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/golf_league

# Backend
SECRET_KEY=your_secret_key_for_jwt
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## πŸš€ Deployment

**Backend** (DigitalOcean Droplet):
- Ubuntu 22.04 droplet ($12/month)
- Docker Compose setup
- Caddy for HTTPS reverse proxy

**Frontend** (Vercel):
- Automatic deployments from main branch
- Environment variables configured in dashboard

## πŸ"§ Development Notes

- **Backend runs on**: http://localhost:8000
- **Frontend runs on**: http://localhost:3000
- **Database runs on**: localhost:5432
- **First user**: Must be manually set as admin in database

## πŸ"ž Support

For issues or questions:
1. Check documentation in `docs/` folder
2. Review `.cursorrules` for conventions
3. Check `IMPLEMENTATION_PLAN.md` for feature details

## πŸ"„ License

MIT License - feel free to use this project as you wish!

---

**Built with**: Next.js, FastAPI, PostgreSQL, and the Free Golf API

