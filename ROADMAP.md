# Golf Pick'em League - Roadmap

## Current Session Status (Feb 21, 2026)

### To Resume
1. **Restart frontend** to see UI changes: `docker-compose restart frontend`
2. **Apply migration** for multi-year tournaments: `docker-compose exec backend alembic upgrade head`
3. **Re-import tournaments** to get Grant Thornton 2026 (the current live tournament)

### Known Issues to Fix Next Session
- [ ] **Past tournaments showing in "Upcoming Tournaments"** - Dashboard filter not working correctly
- [ ] **Create League dropdown shows completed tournaments** - Should only show upcoming/active
- [ ] **Verify team total score displays correctly** on league leaderboard after restart

---

## Recently Completed

- [x] **Round score bug fix** - Per-round scores now display correctly (not cumulative)
- [x] **Mobile text visibility** - Removed dark mode override causing invisible text
- [x] **Tournament unique constraint** - Migration created to allow same tournament for multiple years
- [x] **Standings auto-detection** - API now auto-detects latest round instead of defaulting to round 4
- [x] **UI redesign** - Masters/Augusta inspired theme with classic golf aesthetic
- [x] **Live tournament panel** - ESPN-style sidebar showing active tournament leaderboard
- [x] **League ordering** - Active/upcoming leagues first, completed leagues collapsible
- [x] **Tournament ordering** - API returns ascending by date (upcoming first)
- [x] **Create league from tournament list** - Direct link with tournament pre-selected
- [x] **Improved invite code UX** - Click to copy with visual feedback
- [x] **Data refresh messaging** - "Scores update every 10 minutes during active tournament hours"
- [x] **Current round display** - Shows "Live - Round X" on league pages

---

## Bugs / Critical Fixes

1. **Login error message disappears instantly**
   - Red banner "incorrect user or password" shows briefly then vanishes
   - Should persist until dismissed or new action taken

2. **Tournament filtering incomplete**
   - Dashboard "Upcoming Tournaments" may show past tournaments
   - Create League dropdown should exclude completed tournaments
   - Need to verify frontend filtering logic after backend returns all tournaments

---

## UX Improvements

3. **Draft deadline editing**
   - Ability to change draft deadline after league creation

4. **Tournament display enhancements**
   - Show venue/course info where available
   - Better date formatting throughout

---

## New Features

5. **Password reset**
   - Send reset email to user
   - Requires email service integration

6. **Permission management**
   - Ability to edit permission levels outside owner portal
   - Prevent lockout scenarios
   - Consider self-service role elevation with safeguards

7. **About page**
   - App description and purpose
   - Data source attribution (Live Golf Data API)
   - Developer info and GitHub link
   - Getting started guide
   - How to create a league
   - Permission levels explained
   - Contact information

8. **Custom domain**
   - Configure custom domain for production

---

## Future Enhancements

9. **Player avatar images**
    - Display player initials or photos in roster/standings views
    - Consider sourcing from golf data APIs or allowing uploads

10. **Hole-by-hole progress indicators**
    - Show which hole each player is on during live rounds
    - Visual progress bar or hole number display

11. **Real-time auto-refresh**
    - WebSocket or polling for live score updates
    - Visual indicator when scores are being refreshed

12. **Dark mode toggle**
    - Proper dark mode implementation with user preference
    - System preference detection with manual override

13. **Historical league stats**
    - Win/loss record across leagues
    - Best picks, worst picks analysis
    - Head-to-head records

---

## Technical Notes

### Files Changed This Session
- `backend/app/routes/leagues.py` - Standings auto-detection, league sorting
- `backend/app/routes/tournaments.py` - Live tournament endpoint, ascending order
- `backend/app/models/tournament.py` - Composite unique constraint
- `backend/alembic/versions/20260221_fix_tournament_unique_constraint.py` - Migration
- `frontend/app/dashboard/page.tsx` - Complete redesign with live panel
- `frontend/app/leagues/[id]/page.tsx` - Redesign with round info
- `frontend/app/teams/[id]/page.tsx` - Consistent styling
- `frontend/app/leagues/create/page.tsx` - Tournament pre-selection
- `frontend/app/globals.css` - Masters theme
- `frontend/components/Navbar.tsx` - Dark header
- `frontend/lib/formatScore.ts` - Score formatting utilities
- `frontend/lib/api.ts` - LiveTournament type and endpoint

### Docker Commands
```bash
# Restart frontend only
docker-compose restart frontend

# Apply database migration
docker-compose exec backend alembic upgrade head

# Check migration status
docker-compose exec backend alembic current

# Skip migration if already applied
docker-compose exec backend alembic stamp c8f3a2d1e5b7

# Full rebuild
docker-compose down && docker-compose up --build
```
