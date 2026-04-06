# Golf Pick'em League - Roadmap

## Current Status (Apr 6, 2026)

### Recently Completed (PR #7 — League Enhancements, Apr 2026)
- [x] Pick N, count best M scoring — leagues can configure `scoring_count` (e.g., pick 6, best 3 count)
- [x] League chat — per-league comment section with post/delete
- [x] Profile page (`/profile`) — change username with uniqueness validation
- [x] Team name editing — inline pencil-icon edit on team page
- [x] Draft deadline editing — inline edit for league admin on league page
- [x] "Last updated" on team page now shows actual `last_score_sync` (not page load time)
- [x] Login error message no longer disappears instantly (axios 401 interceptor fix)
- [x] Navbar added to About page
- [x] Tournament date off-by-one fix (`parseLocalDate` utility)
- [x] Dashboard live leaderboard shows `last_score_sync` timestamp
- [x] Fixed Team interface `name` vs `team_name` field mismatch
- [x] Auto-import tournaments on startup for fresh environments

### Completed (PR #6 — PWA, Mar 2026)
- [x] PWA standalone support (`manifest.ts`)

### Earlier Completed
- [x] UI modernization pass — rounded corners, shadows, pill badges, card-based layouts, hover effects
- [x] Typography split — Georgia for display headings, Geist Sans for body/UI
- [x] Inline styles migrated to Tailwind classes + CSS variables
- [x] Consistent theme across all pages (home, login, signup, dashboard, league, team, create, about, admin, join)
- [x] Navbar: shadow, animated mobile menu, pill role badges
- [x] Draft modal: rounded, backdrop blur, bottom-sheet on mobile
- [x] Loading spinner branded green, error messages rounded
- [x] Disable FastAPI docs/redoc/openapi endpoints in production
- [x] Auto-correct stuck tournaments to "completed" on startup
- [x] Public config endpoint (`/api/config/public`) for dynamic sync interval display
- [x] "Last refresh" on league page shows actual score sync time (not page load time)
- [x] Masters green/gold theme on home, login, signup pages
- [x] About / How It Works page (`/about`) with Navbar link
- [x] Past tournaments (Genesis Invitational, Cognizant Classic) no longer stuck as "upcoming"
- [x] API call throttling and playing-hours bug fix
- [x] Suspense boundary and sync error handling for deployment
- [x] Mobile responsive UI
- [x] UI and score display bug fixes
- [x] Masters/Augusta inspired UI redesign
- [x] Live tournament sidebar panel
- [x] League ordering (active first, completed collapsible)
- [x] Create league from tournament list with pre-selection
- [x] Improved invite code UX (click to copy)
- [x] Current round display ("Live - Round X")

---

## UX / UI Improvements

1. **UI redesign / next-level polish**
   - Revisit overall look and feel — explore bolder design directions
   - Consider: page transitions/animations, richer card designs, more distinctive visual identity
   - Potential areas: hero section redesign, leaderboard presentation, dashboard layout
   - Evaluate adding subtle textures, background patterns, or gradient mesh effects
   - Use Playwright for visual testing across pages during iteration

2. **About page — clarify user roles and sign-up flow**
   - Explain that signing up gives you the ability to **join** leagues (via invite code), but not create them
   - To gain the ability to **create leagues**, you need to become a **League Admin**
   - Add a contact form (or mailto link with hidden/obfuscated email) to request League Admin access from the site owner
   - Consider a simple form that sends an email without exposing the address (e.g., serverless function or backend endpoint)

3. **About page — personal section / credits**
   - Section about who built this and why (developer bio / "About Me")
   - Link to GitHub repo
   - Could be a separate section on the existing About page, or a dedicated `/about/developer` page
   - Tech stack overview (Next.js, FastAPI, PostgreSQL, Railway, etc.)

4. **Tournament display enhancements**
   - Show venue/course info where available
   - Better date formatting throughout

---

## New Features

5. **League Admin request flow**
   - Contact form on About page to request League Admin status
   - Backend endpoint to send email to site owner (email hidden from client)
   - Include requester's username and reason
   - Owner receives email and can approve via admin panel

6. **Password reset**
    - Send reset email to user
    - Requires email service integration

7. **Permission management**
    - Ability to edit permission levels outside owner portal
    - Prevent lockout scenarios

8. **Custom domain**
    - Configure custom domain for production

---

## Future Enhancements

9. **Player avatar images**
    - Display player initials or photos in roster/standings views

10. **Hole-by-hole progress indicators**
    - Show which hole each player is on during live rounds

11. **Real-time auto-refresh**
    - WebSocket or polling for live score updates
    - Visual indicator when scores are being refreshed

12. **Dark mode toggle**
    - Proper dark mode with user preference and system detection

13. **Historical league stats**
    - Win/loss record across leagues
    - Best picks, worst picks analysis
    - Head-to-head records

14. **Player Insights — ML-powered predictions and analytics**
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
