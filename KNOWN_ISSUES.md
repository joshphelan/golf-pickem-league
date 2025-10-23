# Known Issues & Status

## 🚨 Critical Issues (Blocking)

### 1. 422 Error on Tournament Schedule Endpoint
**Status**: Active
**Impact**: High - Tournament import not working
**Symptoms**: 
- Frontend shows 422 error when loading tournament dropdown
- Console shows "Request failed with status code 422"
- Tournament import page not functional

**Root Cause**: Authentication issue - JWT token not being sent properly
**Investigation Needed**:
- Check if user is logged in
- Verify JWT token in browser Network tab
- Test schedule endpoint directly: `http://localhost:8000/api/tournaments/schedule`

**Quick Fix**:
1. Ensure user is logged in on frontend
2. Check browser dev tools → Network tab for Authorization header
3. Test endpoint directly with curl/Postman
4. Add better error handling in frontend

## ⚠️ Medium Priority Issues

### 2. User Permission System Confusion
**Status**: Partially Resolved
**Impact**: Medium - New users can't access features
**Symptoms**:
- New users (jane@jane.com, jack@jack.com) can't login
- Error: "user must be approved first"
- Permission levels not clear to users

**Current State**: 
- Users can login but need admin approval for league creation
- Owner portal exists but permission elevation has issues
- 3-tier system implemented but UX needs improvement

**Next Steps**:
- Clarify permission levels in UI
- Fix permission elevation in owner portal
- Add clear messaging about approval process

### 3. Tournament Import UX
**Status**: Partially Resolved
**Impact**: Medium - Manual process required
**Symptoms**:
- No automatic tournament list
- Users need to know tournament IDs
- Import process not user-friendly

**Current State**:
- Schedule dropdown added but has 422 error
- Manual entry fields available
- "Dev/Test Only" warning added

**Next Steps**:
- Fix 422 error on schedule endpoint
- Make dropdown functional
- Consider production tournament sync strategy

## ✅ Recently Fixed Issues

### 4. Backend Startup Hanging
**Status**: ✅ RESOLVED
**Issue**: Backend wouldn't start due to async/sync conflicts
**Fix**: Added asyncio.run() wrapper in scheduler, removed auto-refresh from league creation

### 5. Team Ownership Field Mismatch
**Status**: ✅ RESOLVED
**Issue**: Frontend used `owner_id` but backend used `user_id`
**Fix**: Updated frontend to use `user_id` consistently

### 6. League Creation Performance
**Status**: ✅ RESOLVED
**Issue**: League creation was slow due to auto-refresh
**Fix**: Removed auto-refresh, added manual "Refresh Players" button

### 7. Date/Time Picker UX
**Status**: ✅ RESOLVED
**Issue**: Single datetime input was hard to use
**Fix**: Split into separate date and time inputs

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

1. **Debug 422 Error**
   - Check authentication flow
   - Test schedule endpoint directly
   - Fix JWT token handling

2. **Test Complete Flow**
   - User registration → login → league creation → team drafting
   - Verify all features work end-to-end

3. **Production Readiness**
   - Verify environment configuration
   - Test deployment checklist
   - Document setup process

## 🚀 Success Metrics

- [ ] No 422 errors in console
- [ ] Tournament import works (dropdown or manual)
- [ ] Complete user flow works end-to-end
- [ ] All features accessible to users
- [ ] Production deployment ready

**Current Status**: 80% complete - Main functionality works, authentication issue blocking tournament import.