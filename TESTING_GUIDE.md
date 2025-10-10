# Backend Testing Guide

Quick guide to test all Phase 3 functionality via Swagger UI.

**Total API Calls: 2** (import + sync)

---

## Prerequisites

```bash
# 1. Ensure Docker is running
docker ps

# 2. Start backend (in backend directory)
.\venv\Scripts\activate
uvicorn app.main:app --reload

# 3. Open Swagger UI
# http://localhost:8000/docs
```

---

## Test Flow (30 minutes)

### Step 1: Authentication (No API calls)

**Signup:**
```
POST /api/auth/signup
{
  "username": "yourname",
  "email": "your@email.com",
  "password": "yourpassword123"
}
```
✅ Success: User created (you're automatically primary owner)

**Login:**
```
POST /api/auth/login
{
  "username": "yourname",
  "password": "yourpassword123"
}
```
✅ Success: Copy the `access_token`

**Authorize:**
- Click "Authorize" button at top of Swagger page
- Paste token
- Click "Authorize" then "Close"

---

### Step 2: Import Tournament (1 API call)

```
POST /api/tournaments/import
{
  "tourn_id": "475",
  "year": 2024
}
```

✅ **Success looks like:**
```json
{
  "id": "...",
  "tourn_id": "475",
  "name": "Valspar Championship",
  "year": 2024,
  "start_date": "2024-03-21",
  "end_date": "2024-03-24",
  "timezone": "America/New_York",
  "status": "completed"
}
```

**Copy the tournament `id` (UUID)**

---

### Step 3: Sync Scores (1 API call)

```
POST /api/tournaments/{id}/sync-scores
```
(Replace `{id}` with tournament ID from Step 2)

✅ **Success looks like:**
- Status 200
- Console shows: "Synced scores for tournament Valspar Championship: 150 created, 0 updated"

**Verify in database:**
```sql
-- In pgAdmin or psql
SELECT COUNT(*) FROM player_scores;
-- Should show ~150 records
```

---

### Step 4: Create League (No API calls)

```
POST /api/leagues
{
  "tournament_id": "{tournament_id_from_step_2}",
  "name": "Test League",
  "draft_deadline": "2025-12-31T23:59:59Z",
  "max_members": 10,
  "team_size": 4
}
```

✅ **Success looks like:**
```json
{
  "id": "...",
  "name": "Test League",
  "invite_code": "ABC12345"  // 8 chars
}
```

**Copy the league `id` and `invite_code`**

---

### Step 5: Join League (SKIP if you're the creator)

**⚠️ SKIP THIS STEP** - When you create a league (Step 4), a team is automatically created for you!

**Only use this endpoint if you're testing with a second user:**

**Endpoint:** `POST /api/leagues/join/{invite_code}`

**Query Parameter:**
- `team_name`: Your team name (e.g., "Dream Team")

**Example:**
```
POST /api/leagues/join/ABC12345?team_name=Dream Team
```

✅ **Result:** You already have a team! Proceed to Step 6.

---

### Step 6: Get League Members (Get Your Team ID)

**Endpoint:** `GET /api/leagues/{league_id}/members`

Use the `league_id` from Step 4.

This returns all teams in the league. Find yours and **copy your `team_id`**.

---

### Step 7: Get Available Players

**Endpoint:** `GET /api/teams/{team_id}/available-players`

Use your `team_id` from Step 6.

✅ **Success looks like:**
```json
[
  {
    "id": "...",
    "player_id": "34466",
    "full_name": "Peter Malnati",
    "first_name": "Peter",
    "last_name": "Malnati"
  },
  // ... ~150 players
]
```

**Pick 4 player IDs** (any 4 from the list)

---

### Step 8: Draft Players

**Endpoint:** `POST /api/teams/{team_id}/players`

Repeat this 4 times with different player IDs:

```
POST /api/teams/{team_id}/players
{
  "player_id": "{player_id_from_available_list}"
}
```

✅ **Success each time:** Player added to team

---

### Step 9: View Team Details

**Endpoint:** `GET /api/teams/{team_id}`

```
GET /api/teams/{team_id}
```

✅ **Success looks like:**
```json
{
  "id": "...",
  "team_name": "My Team",
  "players": [
    {
      "player": {
        "full_name": "Peter Malnati"
      }
    }
    // ... 3 more players
  ],
  "total_score": -25  // Sum of 4 player scores!
}
```

**Key check:** `total_score` should be a number (not null)

---

### Step 10: View League Standings

**Endpoint:** `GET /api/leagues/{league_id}/standings`

```
GET /api/leagues/{league_id}/standings?round_num=4
```

✅ **Success looks like:**
```json
{
  "league_name": "Test League",
  "round": 4,
  "standings": [
    {
      "rank": 1,
      "team_name": "My Team",
      "user": "yourname",
      "total_score": -25,
      "players": [
        {
          "player_name": "Peter Malnati",
          "score": -12,
          "position": 1,
          "made_cut": true
        },
        // ... 3 more players with scores
      ]
    }
  ]
}
```

**Key checks:**
- Rank is assigned
- Total score matches sum of player scores
- All 4 players show individual scores

---

## Success Criteria

✅ **Phase 3 is successful if:**

1. Tournament imports with dates and timezone
2. Scores sync from API (150 PlayerScore records created)
3. League created with invite code
4. Team created and 4 players drafted
5. Team detail shows `total_score` (sum of players)
6. Standings show ranked teams with player breakdown
7. **Only 2 API calls used** (import + sync)

---

## Common Issues & Fixes

### "Tournament already exists"
**Solution:** Already imported it! Get tournament ID from:
```
GET /api/tournaments
```

### "No leaderboard data available"
**Cause:** Tournament too recent or future
**Solution:** Use tournId="475", year=2024 (completed tournament)

### "Player already drafted"
**Cause:** Trying to draft same player twice
**Solution:** Pick different player from available list

### "total_score: null" in team details
**Cause:** Players don't have scores yet
**Solution:** Make sure Step 3 (sync scores) completed successfully

### Validation errors on league create
**Cause:** Draft deadline in past or name too short
**Solution:** 
- Use future date: "2025-12-31T23:59:59Z"
- Name must be 3-100 characters

---

## Quick Verification Queries

```sql
-- Check tournaments
SELECT tourn_id, name, status, start_date, timezone FROM tournaments;

-- Check if scores synced
SELECT COUNT(*) FROM player_scores;

-- Check your team's players
SELECT p.full_name, ps.total_score, ps.position
FROM team_players tp
JOIN players p ON tp.player_id = p.id
LEFT JOIN player_scores ps ON ps.player_id = p.id
WHERE tp.team_id = '{your_team_id}';
```

---

## Next Steps After Testing

Once all 9 steps work:
1. ✅ Backend is fully functional
2. ✅ Ready for frontend development
3. Move to Phase 4: Build Next.js frontend

**Estimated frontend time:** 2-3 weeks

