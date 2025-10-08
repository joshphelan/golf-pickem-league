# Golf Fantasy League

Fantasy golf web application where users join private leagues, draft PGA Tour golfers, and compete based on real tournament scores.

## Tech Stack

- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS
- **Backend**: FastAPI + Python 3.11+
- **Database**: PostgreSQL
- **API**: Free Golf API (https://freewebapi.com/sports-apis/golf-api/)

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker Desktop
- Free Golf API key

### Setup

1. **Clone and configure**
   ```bash
   git clone <repo-url>
   cd golf-pickem-league
   cp .env.example .env
   # Add your GOLF_API_KEY and generate SECRET_KEY
   ```

2. **Start backend**
   ```bash
   docker-compose up -d postgres
   cd backend
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Mac/Linux
   pip install -r requirements.txt
   alembic upgrade head
   uvicorn app.main:app --reload
   ```

3. **API available at**
   - http://localhost:8000
   - http://localhost:8000/docs

## Current Status

**Phase 1 Complete**: Backend foundation with authentication and user management

**Next**: Phase 2 - Golf API integration and league management

See `NEXT_STEPS.md` for detailed progress and `IMPLEMENTATION_PLAN.md` for full roadmap.

## Development

- Backend runs on port 8000
- Frontend will run on port 3000
- PostgreSQL on port 5432
- First user to sign up becomes primary owner automatically

## Documentation

- `.cursorrules` - AI coding guidelines
- `IMPLEMENTATION_PLAN.md` - Full 3-week implementation plan
- `NEXT_STEPS.md` - Current progress and immediate tasks
- `backend/README.md` - Backend-specific setup

## License

MIT
