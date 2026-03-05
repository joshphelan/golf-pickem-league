# Golf Pick'em League - Roadmap

## Current Session Status (Mar 4, 2026)

### Recently Completed
- [x] Disable FastAPI docs/redoc/openapi endpoints in production
- [x] Auto-correct stuck tournaments to "completed" on startup
- [x] Public config endpoint (`/api/config/public`) for dynamic sync interval display
- [x] "Last refresh" on league page shows actual score sync time (not page load time)
- [x] Masters green/gold theme on home, login, signup pages
- [x] About / How It Works page (`/about`) with Navbar link
- [x] Past tournaments (Genesis Invitational, Cognizant Classic) no longer stuck as "upcoming"

### Previous Session Fixes
- [x] API call throttling and playing-hours bug fix
- [x] Suspense boundary and sync error handling for deployment
- [x] UI and score display bug fixes
- [x] Round score bug fix — per-round scores display correctly
- [x] Mobile text visibility fix
- [x] Tournament unique constraint for multi-year support
- [x] Standings auto-detection of latest round
- [x] Masters/Augusta inspired UI redesign
- [x] Live tournament sidebar panel
- [x] League ordering (active first, completed collapsible)
- [x] Create league from tournament list with pre-selection
- [x] Improved invite code UX (click to copy)
- [x] Current round display ("Live - Round X")

---

## Bugs / Critical Fixes

1. **"Last updated" on team page still shows page load time**
   - Same issue that was fixed on the league standings page
   - Team detail page (`/teams/[id]`) needs to use actual score sync time from backend
   - Needs `last_score_sync` added to team endpoint response

2. **Login error message disappears instantly**
   - Red banner "incorrect user or password" shows briefly then vanishes
   - Should persist until dismissed or new action taken

3. **Add Navbar to About page**
   - About page currently has no navigation bar
   - Should show the same Navbar as authenticated pages (or a simplified public nav for unauthenticated users)

---

## UX / UI Improvements

4. **UI modernization pass**
   - Current design is too boxy — needs more modern feel
   - Rounded corners, subtle shadows, better spacing and breathing room
   - Smoother transitions and hover states
   - Keep the Masters green/gold/cream color theme
   - Apply consistently across all pages (dashboard, league, team, create, admin)

5. **About page — clarify user roles and sign-up flow**
   - Explain that signing up gives you the ability to **join** leagues (via invite code), but not create them
   - To gain the ability to **create leagues**, you need to become a **League Admin**
   - Add a contact form (or mailto link with hidden/obfuscated email) to request League Admin access from the site owner
   - Consider a simple form that sends an email without exposing the address (e.g., serverless function or backend endpoint)

6. **About page — personal section / credits**
   - Section about who built this and why (developer bio / "About Me")
   - Link to GitHub repo
   - Could be a separate section on the existing About page, or a dedicated `/about/developer` page
   - Tech stack overview (Next.js, FastAPI, PostgreSQL, Railway, etc.)

7. **Draft deadline editing**
   - Ability to change draft deadline after league creation

8. **Tournament display enhancements**
   - Show venue/course info where available
   - Better date formatting throughout

---

## New Features

9. **League Admin request flow**
   - Contact form on About page to request League Admin status
   - Backend endpoint to send email to site owner (email hidden from client)
   - Include requester's username and reason
   - Owner receives email and can approve via admin panel

10. **Password reset**
    - Send reset email to user
    - Requires email service integration

11. **Permission management**
    - Ability to edit permission levels outside owner portal
    - Prevent lockout scenarios

12. **Custom domain**
    - Configure custom domain for production

---

## Future Enhancements

13. **Player avatar images**
    - Display player initials or photos in roster/standings views

14. **Hole-by-hole progress indicators**
    - Show which hole each player is on during live rounds

15. **Real-time auto-refresh**
    - WebSocket or polling for live score updates
    - Visual indicator when scores are being refreshed

16. **Dark mode toggle**
    - Proper dark mode with user preference and system detection

17. **Historical league stats**
    - Win/loss record across leagues
    - Best picks, worst picks analysis
    - Head-to-head records

18. **Player Insights — ML-powered predictions and analytics**
    - **Phase 1: Model & data pipeline**
      - Collect and store historical player/tournament data (course history, recent form, strokes gained, field strength)
      - Build ML model to predict player tournament scores (e.g., XGBoost, LightGBM, or neural net)
      - Train on historical PGA Tour data; retrain periodically as new results come in
      - Backend endpoint to serve predictions per tournament (`GET /api/predictions/{tournament_id}`)
    - **Phase 2: Insights hub page**
      - Dedicated `/insights` page showing predictions for the upcoming tournament
      - Predicted finish range and expected score for each player in the field
      - Model accuracy metrics displayed over time (MAE, predicted vs actual charts, calibration plots)
      - Highlight data science methodology — feature importance, model architecture, training approach
      - Public-facing (no auth required) to showcase data science skills
    - **Phase 3: Integrate into draft experience**
      - "Recommended Picks" panel on the draft page — top predicted value players still available
      - Player cards show predicted score alongside historical stats
      - Risk/upside indicators (high ceiling vs safe floor players)
      - Post-tournament recap comparing predictions vs actuals for your roster
    - **Tech considerations**
      - Model training could run as a scheduled job or separate service
      - Store predictions in DB per tournament so they're auditable after the fact
      - Consider a lightweight Python ML service or run inference directly in the FastAPI backend

---

## Technical Notes

### Docker Commands
```bash
# Restart frontend only
docker-compose restart frontend

# Apply database migration
docker-compose exec backend alembic upgrade head

# Full rebuild
docker-compose down && docker-compose up --build
```
