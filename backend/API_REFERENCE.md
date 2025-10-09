# Live Golf Data API Reference

## Overview
This project uses the **Live Golf Data API** via RapidAPI.

**Base URL**: `https://live-golf-data.p.rapidapi.com`

**Required Headers**:
```
X-RapidAPI-Key: <your_api_key>
X-RapidAPI-Host: live-golf-data.p.rapidapi.com
```

---

## Available Endpoints

### 1. GET /schedule
Get tournament schedule for a year.

**Parameters**:
- `year` (required): Tournament year (e.g., 2024, 2025)

**Response**:
```json
{
  "orgId": 1,
  "year": 2024,
  "schedule": [
    {
      "tournId": "016",
      "name": "The Sentry",
      "date": {
        "start": {"$date": {"$numberLong": "1735776000000"}},
        "end": {"$date": {"$numberLong": "1736035200000"}}
      },
      "venue": "Kapalua Resort (Plantation Course)",
      "purse": "$20,000,000"
    }
  ],
  "timestamp": {...}
}
```

**Usage**: Import tournaments, check tournament dates, auto-detect active tournaments.

---

### 2. GET /tournament
Get tournament details including player field.

**Parameters**:
- `tournId` (required): Tournament ID from schedule (e.g., "475")
- `year` (required): Tournament year

**Response**:
```json
{
  "tournId": "475",
  "name": "Valspar Championship",
  "year": 2024,
  "status": "complete",
  "players": [
    {
      "playerId": "34466",
      "firstName": "Peter",
      "lastName": "Malnati",
      "courseId": "665",
      "status": "complete",
      "isAmateur": false
    }
  ],
  "courses": [...],
  "purse": "$8,100,000",
  "timestamp": {...}
}
```

**Usage**: Get player field for a tournament. DOES NOT include scores.

---

### 3. GET /leaderboard
Get tournament leaderboard with player scores.

**Parameters**:
- `orgId` (required): Organization ID (1 = PGA Tour)
- `tournId` (required): Tournament ID
- `year` (required): Tournament year

**Response**:
```json
{
  "orgId": "1",
  "year": "2024",
  "tournId": "475",
  "status": "Official",
  "roundId": 4,
  "roundStatus": "Official",
  "lastUpdated": "2024-03-24T22:11:32.844Z",
  "cutLines": [{"cutCount": 75, "cutScore": "E"}],
  "leaderboardRows": [
    {
      "playerId": "34466",
      "firstName": "Peter",
      "lastName": "Malnati",
      "position": "1",
      "total": "-12",
      "status": "complete",
      "currentRoundScore": "-4",
      "totalStrokesFromCompletedRounds": "272",
      "rounds": [
        {
          "roundId": 1,
          "scoreToPar": "-5",
          "strokes": 66,
          "courseId": "665"
        }
      ],
      "thru": "F"
    }
  ],
  "timestamp": {...}
}
```

**Usage**: Get player scores for scoring system. Use `total` field for fantasy scoring.

---

## Data Flow

### For Importing a Tournament:
1. Call `/schedule` to get tournament list
2. Call `/tournament` to get player field
3. Store tournament + players in database

### For Syncing Scores:
1. Call `/leaderboard` with orgId=1, tournId, year
2. Extract `leaderboardRows` array
3. For each player, get `total` score
4. Update `PlayerScore` table in database

---

## Important Notes

1. **orgId = 1**: Always use `1` for PGA Tour tournaments
2. **tournId format**: String IDs like "016", "475" (not integers)
3. **Scores location**: ONLY in `/leaderboard`, NOT in `/tournament`
4. **Score format**: String like "-12", "+3", "E" (need to convert for calculations)
5. **Player matching**: Use `playerId` to match between `/tournament` and `/leaderboard`
6. **Tournament status**: Check `status` field ("upcoming", "active", "complete")

---

## Limitations

- `/scorecards` endpoint: Limited to 20 requests/day (hole-by-hole data)
- `/players` search endpoint: Not confirmed available in free tier
- Rate limits: Standard RapidAPI free tier limits apply

---

## Testing

Run `python backend/simple_api_test.py` to test all endpoints and see live data structure.


