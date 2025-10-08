# Golf Fantasy League - Implementation Plan

> Last Updated: October 7, 2025
> API: Free Golf API (https://freewebapi.com/sports-apis/golf-api/)
> Status: Phase 1 Complete

## Overview

Build a fantasy golf web application where users join private leagues, draft PGA Tour golfers, and compete based on combined stroke scores with real-time leaderboard updates.

**Timeline**: 3 weeks
**Tech Stack**: Next.js, FastAPI, PostgreSQL, Free Golf API

## Architecture Decisions

1. **Manual Draft System** - First-come-first-served player selection, no live snake draft
2. **Polling for Updates** - Backend polls API every 2-5min, frontend polls backend every 30-60s
3. **Private Leagues Only** - Shareable invite codes, admin approval required
4. **Stroke-Based Scoring** - Team score = sum of 4 golfers' stroke scores (lower wins)

## Database Schema

### Core Tables

```sql
users (id, email, username, hashed_password, is_approved, is_league_admin, is_owner, is_primary_owner)
tournaments (id, tourn_id, name, year, start_date, end_date, status)
players (id, player_id, first_name, last_name, full_name, country)
player_scores (id, tournament_id, player_id, round, round_score, total_score, position, made_cut)
leagues (id, tournament_id, admin_id, name, invite_code, max_members, team_size, draft_deadline, status)
teams (id, league_id, user_id, team_name)
team_players (id, team_id, player_id, drafted_at)
```

## Implementation Phases

### Phase 1: Backend Foundation (Week 1) - COMPLETE

**Completed:**
- FastAPI project structure with SQLAlchemy models
- PostgreSQL setup with Docker Compose
- Alembic migrations configured
- JWT authentication system
- Three-tier permission system (user/league_admin/owner/primary_owner)
- User signup with automatic primary owner detection
- User management endpoints for owners
- All auth endpoints tested

**Files Created:**
- `backend/app/main.py` - FastAPI application
- `backend/app/config.py` - Settings with environment variables
- `backend/app/database.py` - SQLAlchemy setup
- `backend/app/models/` - User, Tournament, Player, League, Team models
- `backend/app/routes/auth.py` - Authentication endpoints
- `backend/app/schemas/auth.py` - Pydantic request/response models
- `backend/app/utils/auth.py` - JWT token utilities
- `backend/app/utils/dependencies.py` - Auth dependencies
- `backend/requirements.txt` - Python dependencies
- `backend/alembic/` - Database migrations
- `docker-compose.yml` - PostgreSQL service

### Phase 2: Tournament & League Management (Week 1-2) - NEXT

**Golf API Integration:**
- Create `services/golf_api_service.py` with wrapper functions for Free Golf API
- Implement methods: get_schedules(), get_tournament_players(), get_leaderboard()
- Import 2-3 completed tournaments for testing
- Add error handling, retries, and rate limiting

**Tournament Endpoints:**
- `GET /api/tournaments` - List all tournaments
- `GET /api/tournaments/{id}` - Tournament details with field
- `GET /api/tournaments/{id}/leaderboard` - Current standings
- `POST /api/admin/tournaments/sync` - Manual sync from API (admin only)
- `POST /api/admin/tournaments/import` - Import historical data (admin only)

**League Management:**
- `POST /api/leagues` - Create league (league admin only)
  - Generate 8-char alphanumeric invite code
  - Set team_size and draft_deadline
- `GET /api/leagues/{id}` - League details with member list
- `GET /api/leagues/{id}/available-players` - Undrafted players for tournament
- `POST /api/leagues/{invite_code}/join` - Join via invite link

**Team Management:**
- `POST /api/teams` - Create team in league
- `GET /api/teams/{id}` - Get team roster and current score
- `POST /api/teams/{id}/players` - Add player to team (before deadline)
- `DELETE /api/teams/{id}/players/{player_id}` - Remove player (before deadline)

### Phase 3: Scoring & Leaderboard (Week 2)

**Scoring Service:**
```python
def calculate_team_score(team_id: UUID, db: Session) -> int:
    """Sum final stroke scores of all team players"""
    # Get team's players
    # Get tournament for this team
    # Sum total_score for each player
    # Return total (lower is better)
```

**Score Sync:**
- Create `services/score_sync_service.py`
- Use APScheduler to fetch scores every 2-5 minutes during active tournaments
- Update player_scores table with round-by-round data
- Add manual trigger endpoint for testing

**Leaderboard:**
- `GET /api/leagues/{id}/standings` - Calculate and rank all teams
- `GET /api/teams/{id}/score-detail` - Detailed scoring breakdown

### Phase 4: Frontend Development (Week 2-3)

**Next.js Setup:**
- Create Next.js 14 app with TypeScript and Tailwind CSS
- Create API client in `lib/api.ts` with token management
- Set up environment variables

**Pages:**
- `/login` and `/signup` - Authentication forms
- `/dashboard` - User's leagues and stats
- `/admin/users` - Approve users and grant permissions (owner only)
- `/leagues/[id]` - League leaderboard with live standings
- `/teams/[id]` - Team roster builder with player search
- `/join/[code]` - Join league via invite link

**Key Components:**
- `<LeagueStandings>` - Live leaderboard table with auto-refresh
- `<TeamBuilder>` - Player search and roster management
- `<PlayerCard>` - Display player with current score
- `<InviteLink>` - Copy shareable league link
- `<ScoreDisplay>` - Live score with round breakdown

### Phase 5: Deployment (Week 3)

**Backend (DigitalOcean):**
- Create $12/month droplet (Ubuntu 22.04)
- Install Docker and Docker Compose
- Deploy backend with Caddy reverse proxy for HTTPS
- Configure environment variables
- Set up PostgreSQL backups

**Frontend (Vercel):**
- Connect GitHub repository to Vercel
- Configure environment variables (NEXT_PUBLIC_API_URL)
- Deploy with automatic CI/CD

**Final Steps:**
- Update CORS to allow Vercel domain
- Import upcoming PGA tournaments
- Test complete user flow end-to-end
- Create first admin user manually

## API Integration - Free Golf API

**Key Endpoints:**
- `/schedules?year=2025&orgId=1` - PGA Tour schedule
- `/tournaments?tournId=XXX&year=2025` - Tournament metadata and field
- `/leaderboards?tournId=XXX&year=2025&roundId=1` - Live scores
- `/players?lastName=Smith` - Search players

**Data Flow:**
1. Admin imports tournaments via sync endpoint
2. Backend stores tournament and player data
3. APScheduler fetches live scores every 2-5 minutes
4. Scores stored in player_scores table
5. Frontend polls /standings endpoint every 60 seconds
6. Users see updated leaderboard in real-time

## Permission Matrix

| Action | Regular User | League Admin | Owner | Primary Owner |
|--------|-------------|--------------|-------|---------------|
| Join leagues | Yes | Yes | Yes | Yes |
| Draft teams | Yes | Yes | Yes | Yes |
| Create leagues | No | Yes | Yes | Yes |
| Approve users | No | No | Yes | Yes |
| Grant league_admin | No | No | Yes | Yes |
| Grant owner | No | No | Yes | Yes |
| Remove primary owner | No | No | No | No (protected) |

## Success Criteria

**Functional:**
- Users can sign up and get approved
- League admins can create leagues
- Users can join via invite link
- Users can draft 4 golfers before deadline
- Scores sync automatically from Free Golf API
- Leaderboards update in real-time
- Team scores calculated correctly (sum of stroke scores)

**Technical:**
- API response time < 500ms
- Score updates within 5 minutes of Golf API
- Mobile responsive design
- Secure authentication with JWT
- Proper error handling throughout

## Notes

- API key stored in `.env` as `GOLF_API_KEY`
- First user becomes primary owner automatically
- League invite codes are 8-character alphanumeric
- Draft deadline enforced (no changes after)
- Player can only be drafted once per league
- All times in UTC, convert in frontend

## Next Review

After Phase 2 completion
