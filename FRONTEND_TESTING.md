# Frontend Testing Guide

Complete guide for manually testing the Golf Pickem League frontend application.

## Prerequisites

1. **Backend Running**: Make sure the backend is running at `http://localhost:8000`
   ```bash
   cd backend
   venv\Scripts\activate
   uvicorn app.main:app --reload
   ```

2. **Frontend Running**: Start the Next.js dev server
   ```bash
   cd frontend
   npm run dev
   ```

3. **Database Migrated**: Ensure all migrations are applied
   ```bash
   cd backend
   venv\Scripts\activate
   alembic upgrade head
   ```

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
   - "Import Tournament" and "Owner Portal" buttons visible
   - Tournament list visible (owner only)

### Step 4: Import Tournament (Owner Only)
1. Click "Import Tournament" in navbar
2. **Expected**: Tournament import page with:
   - "⚠️ Development/Test Only" warning
   - Tournament dropdown (loads from schedule API)
   - Manual entry fields
   - Existing tournaments list
3. **Test Schedule Dropdown**:
   - Should show list of tournaments from Golf API
   - Select a tournament (e.g., "Valspar Championship 2024")
   - Verify year auto-fills
4. **Test Manual Import**:
   - Tournament ID: `475`
   - Year: `2024`
   - Click "Import Tournament"
5. **Expected**: Success message, then redirected to dashboard
6. **Verify**: Tournament appears in "Tournaments" section with:
   - Name: Valspar Championship
   - Year: 2024
   - Status badge (completed)
   - Dates displayed

### Step 5: Create League
1. On dashboard, click "Create League"
2. Fill in the form:
   - League Name: `Test League`
   - Tournament: Select "Valspar Championship (2024)"
   - Draft Deadline: Choose a future date/time (use improved date/time picker)
   - Team Size: `4`
3. Click "Create League"
4. **Expected**: Redirected to league details page
5. **Verify**:
   - League name displayed: "Test League"
   - Tournament info shown
   - Invite code displayed (8 characters)
   - "Copy" button next to invite code
   - "Sync Scores" and "Refresh Players" buttons visible (you're the owner)
   - Your team listed in standings (auto-created)

### Step 6: Test Draft Functionality
1. Click "🏌️ Draft Your Team" button (large prominent button)
2. **Expected**: Team details page with:
   - Team name and owner
   - "0 / 4 players drafted"
   - "Draft Player" button visible
   - Empty drafted players table
3. Click "Draft Player" button
4. **Expected**: Draft modal opens with player list
5. **Verify**:
   - Search functionality works
   - Player list loads from available players API
   - Players show names and amateur status
6. Search for a player (e.g., type "Malnati")
7. Click "Draft" next to a player
8. **Expected**: 
   - Success message "Player drafted successfully!"
   - Modal closes
   - Player appears in drafted players table with scores
   - "1 / 4 players drafted" counter updates
9. Repeat to draft 3 more players (total 4)
10. **Verify**:
    - All 4 players displayed with round scores
    - Total team score calculated and displayed
    - "Draft Player" button disabled or hidden (team full)

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
   - No "Import Tournament" or "Owner Portal" buttons
   - Tournament list hidden (owner only)
   - "Want to join a league?" section visible

### Step 9: Join League as Regular User
1. On dashboard, find "Want to join a league?" section
2. Enter the invite code from Step 5
3. Click "Join League"
4. **Expected**: Redirected to league details page
5. **Verify**:
   - League info displayed
   - Both teams visible in standings
   - No "Sync Scores" or "Refresh Players" buttons (not the owner)
   - Invite code NOT visible (not the owner)

### Step 10: Second User Drafts Team
1. Click "🏌️ Draft Your Team" button
2. Draft 4 players (different from josh's players)
3. **Expected**: Players drafted successfully
4. **Verify**: Total team score calculated

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

### Step 13: Test Refresh Players Functionality
1. Login as josh (owner)
2. Go to league details page
3. **Verify**: "Refresh Players" button visible (only for upcoming tournaments)
4. Click "Refresh Players" button
5. **Expected**: Success message with number of players refreshed
6. **Verify**: Player field updated (check draft page)

### Step 14: View Final Standings
1. Navigate to league details page
2. **Expected**: Both teams ranked by score
3. **Verify**:
   - Correct ranking (lower score wins)
   - Player breakdowns for both teams
   - Scores accurate
   - Player names and owner names displayed correctly

### Step 15: Test Edge Cases

#### Undraft Player (Before Deadline)
1. As owner of your team, go to team page
2. Click "Remove" button next to a player
3. **Expected**: Player removed, score recalculated

#### Try to Draft Same Player Twice
1. Try to draft a player that's already on another team
2. **Expected**: Error message "Player already drafted in this league"

#### Access Control
1. Try to access another user's team edit
2. **Expected**: Can view but cannot draft/undraft

#### After Draft Deadline
1. Wait for draft deadline to pass (or set past deadline in league)
2. **Expected**: "Draft Player" button disabled/hidden

## Known Issues to Watch For

1. **Draft Player Button**: Should now appear correctly (fixed user_id vs owner_id issue)

2. **Available Players**: The `getAvailablePlayers` call should work with correct tournament_id and league_id

3. **JWT Expiry**: Tokens expire after 30 days. If you get 401 errors, log out and log back in.

4. **CORS**: If you get CORS errors, ensure backend `CORS_ORIGINS` includes `http://localhost:3000`

5. **Date/Time Format**: Draft deadlines should be in local time, verify they display correctly.

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
- [ ] Owner can import tournaments with schedule dropdown
- [ ] User can create league
- [ ] Invite code generated correctly
- [ ] User can join league via code
- [ ] Team drafting works (add players)
- [ ] Undraft works (remove players)
- [ ] Scores sync from API
- [ ] Standings calculate correctly
- [ ] Rankings are accurate (lower score wins)
- [ ] Owner can sync scores
- [ ] Owner can refresh players
- [ ] Non-owners cannot sync scores or refresh players
- [ ] Owner Portal works for user management
- [ ] Protected routes redirect to login
- [ ] Logout clears token
- [ ] Mobile responsive design works
- [ ] No console errors
- [ ] Error messages display properly

## Success Criteria

✅ **Frontend is working** if:
1. All pages load without errors
2. API calls succeed (check Network tab)
3. Authentication flow works end-to-end
4. Leagues can be created and joined
5. Players can be drafted
6. Scores sync and display correctly
7. Standings calculate properly
8. Mobile layout is functional
9. Owner Portal functions correctly
10. Tournament schedule dropdown works

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
- Check backend `/tournaments/{id}/available-players` endpoint
- Verify tournament has players imported
- Check Network tab for API errors

**Scores showing as "N/A"**
- Tournament hasn't been synced yet
- Click "Sync Scores" button
- Verify `/leaderboard` API call succeeded in backend logs

**Draft Player button not visible**
- Check if user owns the team (user_id matches)
- Verify team has space for more players
- Check browser console for errors

## Next Steps After Testing

1. Document any bugs found
2. Fix critical issues
3. Optional: Add toast notifications (instead of alerts)
4. Optional: Add polling for automatic score updates
5. Optional: Deploy to Vercel

## Production Notes

- Tournament import will be automated in production
- Schedule endpoint caches data for 24 hours
- Player refresh runs automatically for tournaments within 14 days
- Manual refresh available for edge cases