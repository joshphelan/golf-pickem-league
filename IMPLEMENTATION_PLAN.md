# Golf Fantasy League - Implementation Plan

> **Last Updated**: October 7, 2025  
> **API**: Free Golf API (https://freewebapi.com/sports-apis/golf-api/)  
> **Status**: Ready to Begin Phase 1

## πŸ"Œ Executive Summary

Build a fantasy golf web application where users join private leagues, manually draft PGA Tour golfers before tournaments, and compete based on combined stroke scores with real-time leaderboard updates.

**Timeline**: 3 weeks  
**Phases**: 5 implementation phases  
**Tech Stack**: Next.js, FastAPI, PostgreSQL, Free Golf API

---

## πŸ—οΈ Architecture Overview

### Core Design Decisions

1. **Manual Draft System** (not live snake draft)
   - First-come-first-served player selection
   - Admin can manually enter teams for offline drafts
   - Duplicate prevention per league

2. **Simplified Real-Time Updates**
   - Backend polls Free Golf API every 2-5 minutes
   - Frontend polls backend every 30-60 seconds
   - No WebSockets/Socket.IO complexity needed

3. **Private Leagues Only**
   - Shareable invite code system
   - Admin approval required for users
   - Admin-only league creation

4. **Stroke-Based Scoring**
   - Team score = sum of 4 golfers' final stroke scores
   - Lower score wins (standard golf)
   - Missed cuts retain positive scores naturally

---

## πŸ"Š Database Schema

### Core Tables

```sql
-- User Management
users (
  id UUID PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  username TEXT UNIQUE NOT NULL,
  hashed_password TEXT NOT NULL,
  is_approved BOOLEAN DEFAULT FALSE,
  is_admin BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
)

-- PGA Tournaments
tournaments (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  tourn_id TEXT UNIQUE,  -- From Free Golf API
  year INT NOT NULL,
  org_id INT,  -- Organization ID (PGA Tour = 1)
  start_date DATE,
  end_date DATE,
  status TEXT,  -- 'upcoming', 'active', 'completed'
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
)

-- PGA Players
players (
  id UUID PRIMARY KEY,
  player_id TEXT UNIQUE,  -- From Free Golf API
  first_name TEXT,
  last_name TEXT,
  full_name TEXT,
  country TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
)

-- Fantasy Leagues
leagues (
  id UUID PRIMARY KEY,
  tournament_id UUID REFERENCES tournaments(id) ON DELETE CASCADE,
  admin_id UUID REFERENCES users(id) ON DELETE SET NULL,
  name TEXT NOT NULL,
  invite_code TEXT UNIQUE NOT NULL,  -- 8-char alphanumeric
  max_members INT DEFAULT 10,
  team_size INT DEFAULT 4,  -- Golfers per team
  status TEXT DEFAULT 'draft',  -- 'draft', 'active', 'completed'
  draft_deadline TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
)

-- User Teams
teams (
  id UUID PRIMARY KEY,
  league_id UUID REFERENCES leagues(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  team_name TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(league_id, user_id)  -- One team per user per league
)

-- Team Rosters
team_players (
  id UUID PRIMARY KEY,
  team_id UUID REFERENCES teams(id) ON DELETE CASCADE,
  player_id UUID REFERENCES players(id) ON DELETE CASCADE,
  drafted_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(team_id, player_id)  -- No duplicate players on same team
)
-- Note: Add constraint to ensure player drafted once per league

-- Tournament Scores
player_scores (
  id UUID PRIMARY KEY,
  tournament_id UUID REFERENCES tournaments(id) ON DELETE CASCADE,
  player_id UUID REFERENCES players(id) ON DELETE CASCADE,
  round INT NOT NULL,  -- 1, 2, 3, 4
  round_score INT,  -- Score for this round
  total_score INT,  -- Running total (e.g., -7)
  position INT,
  made_cut BOOLEAN DEFAULT TRUE,
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(tournament_id, player_id, round)
)
```

---

## πŸš€ Phase 1: Backend Foundation (Week 1)

**Goal**: Set up FastAPI backend with authentication and database

### Tasks

#### 1.1 Project Setup
- [ ] Initialize FastAPI project structure
- [ ] Create `requirements.txt` with dependencies:
  ```
  fastapi
  uvicorn[standard]
  sqlalchemy
  alembic
  psycopg2-binary
  pydantic-settings
  python-jose[cryptography]
  passlib[bcrypt]
  python-multipart
  httpx
  apscheduler
  ```
- [ ] Set up `docker-compose.yml` with PostgreSQL
- [ ] Create `.env.example` template

#### 1.2 Database Setup
- [ ] Create SQLAlchemy models for all tables
- [ ] Configure Alembic for migrations
- [ ] Create initial migration
- [ ] Test database connection

#### 1.3 Authentication System
- [ ] **Endpoint**: `POST /api/auth/signup`
  - Create user with `is_approved=FALSE`
  - Hash password with bcrypt
  - Return success message
  
- [ ] **Endpoint**: `POST /api/auth/login`
  - Check if user is approved
  - Verify password
  - Return JWT token
  
- [ ] **Dependency**: `get_current_user()`
  - Verify JWT token
  - Return user object
  
- [ ] **Dependency**: `require_admin()`
  - Check if user is admin
  - Raise 403 if not

#### 1.4 Admin Management
- [ ] **Endpoint**: `GET /api/admin/users`
  - List all users with approval status
  - Admin only
  
- [ ] **Endpoint**: `PATCH /api/admin/users/{id}`
  - Toggle `is_approved` or `is_admin`
  - Admin only

**Deliverables**:
- Working FastAPI backend
- Database migrations
- Auth system with JWT
- Admin user management

---

## πŸ"… Phase 2: Tournament & League Management (Week 1-2)

**Goal**: Integrate Free Golf API and build league system

### Tasks

#### 2.1 Free Golf API Integration

Create `services/golf_api_service.py`:

```python
import httpx
from typing import List, Dict, Optional

class GolfAPIService:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {"X-API-Key": api_key}
    
    async def get_schedules(self, year: int, org_id: int = 1) -> List[Dict]:
        """Fetch PGA Tour schedule for year"""
        pass
    
    async def get_tournament_players(self, tourn_id: str, year: int) -> List[Dict]:
        """Fetch players in a tournament"""
        pass
    
    async def get_leaderboard(self, tourn_id: str, year: int, round_id: int) -> Dict:
        """Fetch current leaderboard"""
        pass
    
    async def get_player_scorecard(
        self, tourn_id: str, year: int, player_id: str, round_id: int
    ) -> Dict:
        """Fetch detailed scorecard"""
        pass
```

- [ ] Implement all API methods
- [ ] Add error handling and retries
- [ ] Create function to import historical tournaments
- [ ] Import 2-3 completed tournaments for testing

#### 2.2 Tournament Endpoints
- [ ] **GET** `/api/tournaments` - List all tournaments
- [ ] **GET** `/api/tournaments/{id}` - Tournament details + field
- [ ] **GET** `/api/tournaments/{id}/leaderboard` - Current standings
- [ ] **POST** `/api/admin/tournaments/sync` - Manual sync from API (admin only)
- [ ] **POST** `/api/admin/tournaments/import` - Import historical data (admin only)

#### 2.3 League Management
- [ ] **POST** `/api/leagues` - Create league (admin only)
  - Generate 8-char alphanumeric invite code
  - Set team_size (default 4)
  - Set draft_deadline
  - Validate tournament exists
  
- [ ] **GET** `/api/leagues/{id}` - League details
  - Include member list
  - Include tournament info
  - Show available spots
  
- [ ] **GET** `/api/leagues/{id}/available-players` - Undrafted players
  - Exclude already drafted players in this league
  - Filter by tournament
  
- [ ] **POST** `/api/leagues/{invite_code}/join` - Join via invite link
  - Validate invite code
  - Check league capacity
  - Create team for user
  - Check if user already in league

#### 2.4 Team Management
- [ ] **POST** `/api/teams` - Create team in league
  - Validate user not already in league
  
- [ ] **GET** `/api/teams/{id}` - Get team roster + current score
  
- [ ] **POST** `/api/teams/{id}/players` - Add player to team
  - Validate before draft_deadline
  - Validate player not drafted in league
  - Validate team not full (< team_size)
  - Add player to team_players
  
- [ ] **DELETE** `/api/teams/{id}/players/{player_id}` - Remove player
  - Only before draft_deadline

**Deliverables**:
- Free Golf API integration working
- Historical tournament data imported
- League creation and joining working
- Team roster management functional

---

## πŸ"ˆ Phase 3: Scoring & Leaderboard (Week 2)

**Goal**: Implement scoring calculations and real-time updates

### Tasks

#### 3.1 Scoring Service

Create `services/scoring_service.py`:

```python
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Dict, List

def calculate_team_score(team_id: UUID, db: Session) -> int:
    """
    Calculate team score as sum of all golfers' stroke scores.
    Lower score wins (standard golf scoring).
    """
    # Get team's players
    team_players = db.query(TeamPlayer).filter(
        TeamPlayer.team_id == team_id
    ).all()
    
    # Get tournament for this team
    team = db.query(Team).get(team_id)
    tournament_id = db.query(League).get(team.league_id).tournament_id
    
    total_score = 0
    for tp in team_players:
        # Get latest score for player
        latest_score = db.query(PlayerScore).filter(
            PlayerScore.tournament_id == tournament_id,
            PlayerScore.player_id == tp.player_id
        ).order_by(PlayerScore.round.desc()).first()
        
        if latest_score and latest_score.total_score:
            total_score += latest_score.total_score
    
    return total_score

def get_league_standings(league_id: UUID, db: Session) -> List[Dict]:
    """
    Get ranked standings for all teams in league.
    Returns list sorted by score (ascending = best).
    """
    pass
```

- [ ] Implement `calculate_team_score()`
- [ ] Implement `get_league_standings()`
- [ ] Handle edge cases (missed cuts, withdrawals)
- [ ] Add caching for performance

#### 3.2 Score Sync System

Create `services/score_sync_service.py`:

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

async def sync_tournament_scores(tournament_id: UUID, db: Session):
    """Fetch latest scores from Free Golf API and update database"""
    # Get tournament details
    # Fetch leaderboard from API
    # Update player_scores table
    # Log any errors
    pass

def start_score_sync_scheduler():
    """Start background job to sync scores every 2-5 minutes"""
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        sync_active_tournaments,
        'interval',
        minutes=2,
        id='score_sync'
    )
    scheduler.start()
```

- [ ] Implement score sync logic
- [ ] Add APScheduler configuration
- [ ] Create endpoint to manually trigger sync
- [ ] Add logging for sync operations

#### 3.3 Leaderboard Endpoints
- [ ] **GET** `/api/leagues/{id}/standings` - League leaderboard
  - Calculate all team scores
  - Rank teams (ascending)
  - Include: team_name, user, golfers, total_score, rank
  - Add round-by-round breakdown

- [ ] **GET** `/api/teams/{id}/score-detail` - Detailed team scoring
  - Show each golfer's contribution
  - Round-by-round breakdown
  - Position in tournament

**Deliverables**:
- Scoring calculations working
- Automated score syncing
- League standings endpoint
- Real-time updates (via polling)

---

## 🎨 Phase 4: Frontend Development (Week 2-3)

**Goal**: Build Next.js frontend with all user interfaces

### Tasks

#### 4.1 Next.js Setup
- [ ] Create Next.js 14 app with TypeScript
- [ ] Install dependencies: `tailwindcss`, `axios`, `date-fns`
- [ ] Configure Tailwind CSS
- [ ] Set up environment variables

#### 4.2 API Client Layer

Create `lib/api.ts`:

```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL;

export async function login(email: string, password: string) {
  const res = await fetch(`${API_URL}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  return res.json();
}

export async function getLeagueStandings(leagueId: string) {
  const token = localStorage.getItem('token');
  const res = await fetch(`${API_URL}/api/leagues/${leagueId}/standings`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return res.json();
}

// ... more API functions
```

- [ ] Implement all API client functions
- [ ] Add token management
- [ ] Add error handling
- [ ] Create TypeScript interfaces for responses

#### 4.3 Pages

**Authentication**
- [ ] `/login` - Login form
- [ ] `/signup` - Signup form with approval message
- [ ] Implement redirect after login

**Dashboard**
- [ ] `/dashboard` - User's leagues list
- [ ] Show active/upcoming/completed leagues
- [ ] Quick stats (current rank, etc.)

**League Management**
- [ ] `/leagues/[id]` - League leaderboard
  - Real-time standings table
  - Refresh every 60 seconds
  - Show tournament info
  
- [ ] `/join/[code]` - Join league via invite
  - Validate code
  - Show league info
  - Create team on accept

**Team Management**
- [ ] `/teams/[id]` - Team roster builder
  - Search available players
  - Add/remove players (before deadline)
  - Show current lineup
  - Display team score

**Admin**
- [ ] `/admin/users` - Approve users
- [ ] `/admin/leagues/create` - Create league form
- [ ] `/admin/tournaments` - Sync/import tournaments

#### 4.4 Key Components

- [ ] `<LeagueStandings>` - Sortable standings table
- [ ] `<TeamBuilder>` - Player search and selection
- [ ] `<PlayerCard>` - Display player with stats
- [ ] `<InviteLink>` - Copy invite link button
- [ ] `<ScoreDisplay>` - Live score with round breakdown
- [ ] `<TournamentInfo>` - Tournament details card

#### 4.5 Polish
- [ ] Add loading states
- [ ] Add error handling
- [ ] Responsive design (mobile-friendly)
- [ ] Add toast notifications
- [ ] Implement auto-refresh for leaderboards

**Deliverables**:
- Complete Next.js application
- All user flows working
- Mobile-responsive design
- Connected to backend API

---

## πŸš€ Phase 5: Deployment (Week 3)

**Goal**: Deploy to production

### Tasks

#### 5.1 Backend Deployment (DigitalOcean)

- [ ] Create DigitalOcean Droplet ($12/month, Ubuntu 22.04)
- [ ] Install Docker and Docker Compose
- [ ] Clone repository to server
- [ ] Create production `.env` file
- [ ] Set up PostgreSQL backups
- [ ] Configure Caddy for HTTPS

`Caddyfile`:
```
api.yourdomain.com {
    reverse_proxy backend:8000
}
```

- [ ] Start services: `docker-compose up -d`
- [ ] Run migrations: `alembic upgrade head`
- [ ] Create first admin user manually
- [ ] Test all endpoints

#### 5.2 Frontend Deployment (Vercel)

- [ ] Push code to GitHub
- [ ] Connect repository to Vercel
- [ ] Configure environment variables:
  - `NEXT_PUBLIC_API_URL=https://api.yourdomain.com`
- [ ] Deploy and test
- [ ] Set up custom domain (optional)

#### 5.3 Final Configuration

- [ ] Update CORS in FastAPI to allow Vercel domain
- [ ] Test full user flow end-to-end
- [ ] Import upcoming PGA tournaments
- [ ] Create test league for validation
- [ ] Set up monitoring/logging

**Deliverables**:
- Live production application
- Backend on DigitalOcean
- Frontend on Vercel
- SSL/HTTPS configured
- Ready for users!

---

## βœ… Success Criteria

### Functional Requirements
- βœ… Users can sign up and get approved
- βœ… Admins can create leagues
- βœ… Users can join leagues via invite link
- βœ… Users can draft 4 golfers before deadline
- βœ… Scores sync automatically from Free Golf API
- βœ… Leaderboards update in real-time
- βœ… Team scores calculated correctly

### Technical Requirements
- βœ… API response time < 500ms
- βœ… Score updates within 5 minutes of API
- βœ… Mobile responsive design
- βœ… Secure authentication with JWT
- βœ… Database properly indexed
- βœ… Error handling throughout

---

## πŸ"‹ Next Steps

See **NEXT_STEPS.md** for current action items and division of responsibilities.

---

## πŸ" Notes

- **API Rate Limits**: Free Golf API has rate limits - implement caching
- **Time Zones**: All times in UTC, convert in frontend
- **Scoring Edge Cases**: Handle WD (withdrawal), DQ (disqualified), CUT
- **Testing Data**: Use completed 2024 tournaments for development
- **Future Features**: Consider adding chat, player stats, historical records

---

**Last Reviewed**: October 7, 2025  
**Next Review**: After Phase 1 completion

