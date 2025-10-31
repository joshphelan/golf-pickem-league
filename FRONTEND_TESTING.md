# Frontend Testing Guide

**Last Updated**: October 31, 2024  
**Status**: Updated to match current implementation after Oct 31 bug fixes

Complete guide for manually testing the Golf Pickem League frontend application.

## Prerequisites

1. **Backend Running**: Make sure the backend is running at `http://localhost:8000`
   ```bash
   cd backend
   venv\Scripts\activate  # Windows: venv\Scripts\activate | Mac/Linux: source venv/bin/activate
   uvicorn app.main:app --reload
   ```

2. **Frontend Running**: Start the Next.js dev server
   ```bash
   cd frontend
   npm run dev
   ```

3. **Database Migrated & Tournaments Imported**: Ensure all migrations are applied and test tournaments imported
   ```bash
   cd backend
   venv\Scripts\activate
   alembic upgrade head
   
   # Import test tournaments (first 5 + last 5 from 2025)
   python scripts/import_2025_tournaments.py
   
   # Sync scores for completed tournaments
   python scripts/sync_completed_scores.py
   ```

## ⚠️ Important: Golf API Limitation

The Golf API does NOT provide player data until ~1 week before tournament start. 

**For Testing**: Use only the **past tournaments** (Jan-Feb 2025) which have player data:
- Valspar Championship (2024-03-20) - 80 players
- The Sentry (2025-01-01) - 59 players
- Sony Open in Hawaii (2025-01-08) - 143 players
- The American Express (2025-01-15) - 156 players
- Farmers Insurance Open (2025-01-21) - 155 players
- AT&T Pebble Beach Pro-Am (2025-01-29) - 80 players

**Do NOT use** future tournaments (Nov-Dec 2025) - they have 0 players.

## Test Flow

### Step 1: Landing Page
1. Navigate to `http://localhost:3000`
2. **Expected**: Landing page with "Golf Pickem League" heading
3. **Verify**: 
   - Login and Sign Up buttons visible
   - Three feature cards displayed
   - Responsive design on mobile

### Step 2: Sign Up (First User - Auto-Owner)
1. Click "Sign Up" button
2. Fill in the form:
   - Email: `josh@josh.com`
   - Username: `josh`
   - Password: `password123` (at least 8 characters)
   - Confirm Password: `password123`
3. Click "Sign Up"
4. **Expected**: Success message "Account created successfully. You are the primary owner with full admin access!"
5. Click "Go to Login"

### Step 3: Login as Primary Owner
1. On login page, enter credentials:
   - Email: `josh@josh.com`
   - Password: `password123`
2. Click "Login"
3. **Expected**: Redirected to dashboard
4. **Verify**:
   - Navbar shows username and "(Owner)" badge
   - "Owner Portal" button visible
   - **NOTE**: "Import Tournament" UI has been removed (tournaments imported via script)

### Step 4: Verify Tournaments Imported
1. On dashboard, check that tournaments are listed
2. **Expected**: Should see 6 past tournaments available for league creation:
   - Valspar Championship (2024)
   - The Sentry (2025)
   - Sony Open in Hawaii (2025)
   - The American Express (2025)
   - Farmers Insurance Open (2025)
   - AT&T Pebble Beach Pro-Am (2025)
3. **If tournaments missing**: Run `python scripts/import_2025_tournaments.py` from backend directory

### Step 5: Create League
1. On dashboard, click "Create League"
2. Fill in the form:
   - League Name: `Test League`
   - Tournament: Select "Valspar Championship (2024)" or any other **past tournament**
   - Draft Deadline: Choose a future date/time
   - Team Size: `4`
3. Click "Create League"
4. **Expected**: Redirected to league details page
5. **Verify**:
   - League name displayed: "Test League"
   - Tournament info shown
   - Invite code displayed (8 characters)
   - "Copy" button next to invite code
   - Your team listed in standings (auto-created)

### Step 6: Test Draft Functionality
1. Click your team link from the league standings
2. **Expected**: Team details page with:
   - Team name displayed at top
   - "0 / 4 players drafted" counter
   - "Draft Player" button visible
   - Empty drafted players table with columns: Player, R1, R2, R3, R4, Total, Actions
3. Click "Draft Player" button
4. **Expected**: Draft modal opens with:
   - Modal header showing "Team: X / 4 players (Y slots remaining)"
   - Search bar
   - Player list with names
5. **Verify**:
   - Search functionality works (type part of player name)
   - Player list shows full names
   - Draft buttons are enabled
6. Click "Draft" next to a player
7. **Expected**: 
   - Success message "Player drafted successfully!"
   - Player appears in drafted players table
   - Player name displays in "Player" column (was previously blank - **fixed**)
   - "1 / 4 players drafted" counter updates
   - If tournament is completed, R1-R4 scores display (was previously blank - **fixed**)
8. Repeat to draft 3 more players (total 4)
9. **Expected after 4th player**:
   - Modal auto-closes (was not happening - **fixed**)
   - Success message: "Player drafted! Your team is now full."
   - Draft buttons in modal become disabled with "Full" text (was not disabled - **fixed**)
10. **Verify**:
    - All 4 players displayed with **names visible** in Player column
    - Round scores (R1-R4) displayed for completed tournaments
    - Total team score calculated and displayed
    - "Draft Player" button on main page is **hidden/disabled** (team full)

### Step 7: Create Second User (Regular User)
1. Logout (click Logout button in navbar)
2. Navigate to signup page
3. Create second user:
   - Email: `jane@jane.com`
   - Username: `jane`
   - Password: `password123`
4. Sign up
5. **Expected**: Success message "Account created successfully. You can log in and join leagues."
6. Click "Go to Login"

### Step 8: Login as Regular User
1. Login as jane
2. **Expected**: Redirected to dashboard
3. **Verify**:
   - Navbar shows username (no badges)
   - No "Owner Portal" button (owner only)
   - "Want to join a league?" section visible

### Step 9: Join League as Regular User
1. On dashboard, find "Want to join a league?" section
2. Enter the invite code from Step 5
3. Click "Join League"
4. **Expected**: Redirected to league details page
5. **Verify**:
   - League info displayed
   - Both teams visible in standings
   - Invite code visible (all league members can see it to share)

### Step 10: Second User Drafts Team
1. Click your team link from the standings
2. Draft 4 players (different from josh's players)
3. **Expected**: Players drafted successfully
4. **Verify**: 
   - Player names display correctly
   - Total team score calculated
   - Cannot draft players already on josh's team

### Step 11: Test Owner Portal (Owner Only)
1. Logout and login as josh (owner)
2. Click "Owner Portal" in navbar
3. **Expected**: Owner Portal page with:
   - List of all users
   - User management controls
4. **Test User Management**:
   - Find jane in the user list
   - Toggle "League Admin" ON for jane
   - **Expected**: Success message and jane's status updates
5. **Verify**: jane now has League Admin privileges

### Step 12: Test League Admin Capabilities
1. Logout and login as jane (now League Admin)
2. **Expected**: Dashboard shows "League Admin" badge
3. **Verify**: jane can now create leagues (test this if desired)

### Step 13: Test Remove Player Functionality
1. Login as josh (owner)
2. Go to your team page
3. **Verify**: "Remove" button visible next to each drafted player
4. Click "Remove" button next to a player
5. **Expected**: 
   - Success message "Player removed from team"
   - Player disappears from table
   - Player count updates (e.g., "3 / 4 players drafted")
   - Total team score recalculates
   - "Draft Player" button becomes enabled again
6. **Verify**: Removed player is now available in draft modal again

### Step 14: View Final Standings
1. Navigate to league details page
2. **Expected**: Both teams ranked by score
3. **Verify**:
   - Correct ranking (lower score wins)
   - Player breakdowns for both teams
   - Scores accurate
   - Player names and owner names displayed correctly

### Step 15: Test Edge Cases

#### Try to Draft Same Player Twice
1. Try to draft a player that's already on another team
2. **Expected**: Error message "Player already drafted in this league"

#### Access Control
1. Try to access another user's team edit
2. **Expected**: Can view but cannot draft/undraft

#### After Draft Deadline
1. Wait for draft deadline to pass (or set past deadline in league)
2. **Expected**: "Draft Player" button disabled/hidden

## ✅ Recently Fixed Issues (Oct 31, 2024)

1. **✅ UUID Validation Error**: Fixed draft/undraft sending wrong player ID format (player.id instead of player.player_id)
2. **✅ Player Names Blank**: Fixed nested data structure - now displays teamPlayer.player.full_name
3. **✅ Remove Button Not Working**: Fixed to send correct player UUID
4. **✅ Round Scores Not Showing**: Backend now includes PlayerScore data in team API response
5. **✅ Draft Limit Not Enforced**: Buttons now disabled when team reaches 4 players, modal auto-closes
6. **✅ SSR localStorage Errors**: Added typeof window checks to all localStorage calls
7. **✅ Table Layout**: Player column wider, score columns narrower and centered

## Known Issues to Watch For

1. **JWT Expiry**: Tokens expire after 30 days. If you get 401 errors, log out and log back in.

2. **CORS**: If you get CORS errors, ensure backend `CORS_ORIGINS` includes `http://localhost:3000`

3. **Date/Time Format**: Draft deadlines should be in local time, verify they display correctly.

4. **Golf API Limitation**: Future tournaments (>1 week away) will have 0 players. This is expected API behavior.

## Browser Console Checks

Open Developer Tools (F12) and check:
- **Console**: No JavaScript errors
- **Network**: All API calls return 200/201 (except expected 400/401 errors)
- **Application > Local Storage**: JWT token stored correctly

## Performance Notes

- Page load times should be < 1 second
- API calls should complete in < 2 seconds
- Draft modal should open instantly
- Search filtering should be real-time

## Checklist

- [ ] Landing page loads correctly
- [ ] Signup creates user successfully
- [ ] Login works with valid credentials
- [ ] Dashboard shows appropriate content based on user role
- [ ] Tournaments imported via script (6 past tournaments with players)
- [ ] User can create league with past tournament
- [ ] Invite code generated correctly
- [ ] User can join league via code
- [ ] Team drafting works (add players)
- [ ] Player names display correctly in table
- [ ] Round scores (R1-R4) display for completed tournaments
- [ ] Remove player works (undraft)
- [ ] Draft buttons disable when team is full (4 players)
- [ ] Modal auto-closes when 4th player drafted
- [ ] Standings calculate correctly
- [ ] Rankings are accurate (lower score wins)
- [ ] Owner Portal works for user management
- [ ] Protected routes redirect to login
- [ ] Logout clears token
- [ ] No localStorage SSR errors
- [ ] No console errors
- [ ] Error messages display properly

## Success Criteria

✅ **Frontend is working** if:
1. All pages load without errors or SSR issues
2. API calls succeed (check Network tab)
3. Authentication flow works end-to-end
4. Leagues can be created and joined
5. Players can be drafted with proper UUID handling
6. Player names display correctly (not blank)
7. Round scores (R1-R4) display for completed tournaments
8. Remove player button works
9. Draft limit enforced (buttons disabled at 4 players)
10. Standings calculate properly
11. Mobile layout is functional
12. Owner Portal functions correctly

## Troubleshooting

**"Network Error" in browser console**
- Check backend is running: `http://localhost:8000/docs`
- Verify `.env.local` has correct `NEXT_PUBLIC_API_URL`

**"401 Unauthorized" errors**
- Token expired or invalid
- Log out and log back in
- Clear localStorage if needed

**"Cannot read property of undefined"**
- API response structure might differ from expected
- Check browser console for specific error
- Verify backend is returning correct data format

**Players not loading in draft modal**
- Check if tournament is >1 week away (Golf API limitation - use past tournaments)
- Verify tournament has players: Run `python scripts/import_2025_tournaments.py`
- Check backend `/tournaments/{id}/available-players?league_id=XXX` endpoint
- Check Network tab for API errors

**Player names showing as blank**
- This was fixed Oct 31, 2024
- Ensure backend is running latest code
- Clear browser cache and refresh
- Check frontend is using `teamPlayer.player.full_name`

**Scores showing as "-"**
- Tournament needs score sync: Run `python scripts/sync_completed_scores.py`
- Only completed tournaments have scores
- Future tournaments won't have scores until they complete

**Draft Player button not visible or disabled**
- Team may be full (4 players) - this is correct behavior
- Check browser console for errors
- Verify user owns the team

## Next Steps After Testing

1. Document any new bugs found in `KNOWN_ISSUES.md`
2. Fix critical issues before production
3. Test with multiple users in same league
4. Verify standings calculation accuracy
5. Set up production environment variables
6. Deploy to production (see `PRODUCTION_CHECKLIST.md`)

## Production Notes

- Tournament import will be automated via scheduler (currently manual via scripts)
- Player data refresh needed weekly for tournaments <2 weeks away
- Score sync runs after tournaments complete
- Golf API has 2000 requests/month limit - plan scheduler jobs carefully