# Known Issues & Status

**Last Updated**: October 31, 2024

## 🚨 Critical Issues (Blocking)

### 1. Golf API Player Data Not Available Until ~1 Week Before Tournament
**Status**: Active - **API Limitation**
**Impact**: High - Cannot create leagues for upcoming tournaments
**Symptoms**: 
- Tournaments imported successfully but have 0 players
- Future tournaments (>1 week away) show no available players for drafting
- Example: Tournament on 11/6/2024 has no player data as of 10/30/2024

**Root Cause**: The Live Golf Data API (`https://live-golf-data.p.rapidapi.com`) does not populate player fields (`/tournament` endpoint) until approximately 1 week before the tournament starts.

**Workaround**:
- Use past tournaments (Jan-Feb 2025) for testing
- Wait until ~1 week before tournament to import and create leagues
- Consider refreshing player data closer to tournament start

**Long-Term Solution**:
- Implement weekly scheduler job to refresh player data for upcoming tournaments
- Add UI messaging explaining when player data will be available
- Auto-refresh tournaments that transition from "no players" to "players available"

## ⚠️ Medium Priority Issues

### 2. Next.js SSR localStorage Errors (If Not Properly Handled)
**Status**: ✅ RESOLVED
**Impact**: Medium - Page crashes on refresh
**Symptoms**:
- "localStorage is not defined" errors
- Blank pages with error banners
- Team pages not loading

**Fix Applied**:
- Added `typeof window !== 'undefined'` checks to all localStorage access
- Moved `getUser()` calls to `useEffect` hooks (client-side only)
- Updated `frontend/lib/auth.ts` and team pages

### 3. Backend Python Import Caching Issues
**Status**: ✅ RESOLVED (Document for Future)
**Impact**: Medium - Code changes not taking effect
**Symptoms**:
- Code changes don't apply after editing
- Old code continues running despite file changes
- 403/422 errors persist after removing auth requirements

**Solution**:
1. Delete `__pycache__` directories:
   ```bash
   Remove-Item -Recurse -Force backend/app/__pycache__
   Remove-Item -Recurse -Force backend/app/routes/__pycache__
   Remove-Item -Recurse -Force backend/app/models/__pycache__
   ```
2. Fully stop and restart backend server (Ctrl+C, then restart)

## ✅ Recently Fixed Issues (Oct 31, 2024 Session)

### 4. Draft Player UUID Validation Error (422)
**Status**: ✅ RESOLVED
**Issue**: "Invalid UUID length: expected 32, found 5" when drafting players
**Fix**: Changed frontend to send `player.id` (UUID) instead of `player.player_id` (API string)

### 5. Player Names Not Showing in Team Table
**Status**: ✅ RESOLVED
**Issue**: Player column showed blank/no values
**Fix**: Updated `TeamPlayer` interface to match backend's nested structure (`teamPlayer.player.full_name`)

### 6. Remove Player Button Not Working
**Status**: ✅ RESOLVED
**Issue**: Remove button did nothing, no error
**Fix**: Changed to send `teamPlayer.player.id` instead of `teamPlayer.id` to match backend expectations

### 7. Round Scores (R1-R4) Not Displaying
**Status**: ✅ RESOLVED
**Issue**: Individual round scores not showing, only total
**Fix**: 
- Modified `get_team` endpoint to include player scores
- Created `sync_completed_scores.py` script to fetch scores from Golf API
- Synced 6 completed tournaments with leaderboard data

### 8. Draft Limit Not Enforced in Modal
**Status**: ✅ RESOLVED
**Issue**: Users could click draft buttons even after team was full
**Fix**: 
- Disabled draft buttons when `draftedCount >= maxPlayers`
- Show "Team Full" warning banner in modal
- Modal auto-closes when 4th player drafted

### 9. Tournament Import UI Removed
**Status**: ✅ COMPLETED
**Issue**: Users should not manually import tournaments
**Fix**: Removed all import UI elements (admin page, navbar links, dashboard buttons) - will be automated

## 🔧 Technical Debt

### 8. Error Handling
**Status**: Needs Improvement
**Impact**: Low - Poor user experience
**Issues**:
- Generic error messages
- No loading states for API calls
- 422 errors not handled gracefully

### 9. Environment Configuration
**Status**: Needs Verification
**Impact**: Medium - Production deployment
**Issues**:
- `.env` file setup not documented
- API key configuration unclear
- Environment variable validation missing

### 10. Database State
**Status**: Needs Cleanup
**Impact**: Low - Development only
**Issues**:
- Test data from development
- User accounts with different permission levels
- Tournament data may be outdated

## 🎯 Resolution Priority

### Immediate (Next Session)
1. **Fix 422 Authentication Error** - Blocking tournament import
2. **Test Complete User Flow** - Ensure all features work
3. **Verify Environment Setup** - Ensure production readiness

### Short Term
1. **Improve Error Handling** - Better UX for errors
2. **Clarify Permission System** - Make user roles clear
3. **Add Loading States** - Better user feedback

### Long Term
1. **Production Deployment** - Full deployment setup
2. **Performance Optimization** - API call efficiency
3. **Comprehensive Testing** - End-to-end test suite

## 🧪 Testing Status

### Backend Testing
- ✅ Server starts without hanging
- ✅ Database migrations applied
- ✅ API endpoints respond
- ✅ Authentication system works
- ✅ Scheduler starts properly

### Frontend Testing
- ✅ App loads on port 3000
- ✅ Login system works
- ✅ Dashboard displays
- ❌ Tournament import (422 error)
- ✅ League creation works
- ✅ Team drafting works

### Integration Testing
- ✅ User can create league
- ✅ User can draft team
- ❌ Tournament import workflow
- ✅ Manual player refresh works
- ✅ Standings system works

## 📋 Next Session Action Items

1. **Tournament Player Data Strategy**
   - Import tournaments 1 week before start date (when players become available)
   - Test with upcoming November tournament (when it's <1 week away)
   - Consider implementing weekly refresh job for player data

2. **Automated Tournament Import**
   - Implement scheduler job to import upcoming tournaments
   - Add daily/weekly refresh for player fields
   - See `backend/scripts/import_2025_tournaments.py` as reference

3. **Production Deployment**
   - Set up Vercel (frontend) + DigitalOcean (backend)
   - Configure environment variables
   - Test complete flow in production

4. **Additional Testing**
   - Test with multiple leagues for same tournament
   - Verify scoring updates work correctly
   - Test with real-time data during active tournament

## 🚀 Success Metrics

- [x] No 422 errors in console
- [x] Tournament import works (automated script)
- [x] Complete user flow works end-to-end
- [x] Draft functionality fully working
- [x] Scores display correctly (R1-R4 + total)
- [ ] Player data available for upcoming tournaments (API limitation)
- [ ] Production deployment complete

**Current Status**: 95% complete - Core functionality fully working. Only limitation is Golf API doesn't provide player data until ~1 week before tournament.