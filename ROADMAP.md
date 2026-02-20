# Golf Pick'em League - Roadmap

## Bugs / Critical Fixes

1. **League scores not displaying correctly for incomplete rounds**
   - On leagues page: shows "n/a" for score and "-" by each player
   - Team page shows round 1 scores and total correctly
   - Issue: score aggregation logic doesn't handle partial round data

2. **Login error message disappears instantly**
   - Red banner "incorrect user or password" shows briefly then vanishes
   - Should persist until dismissed or new action taken

## UX Improvements

3. **Tournament ordering**
   - Show in ascending order by date (most upcoming at top)
   - Past tournaments at bottom or hidden entirely

4. **League creation dropdown**
   - Sort tournaments ascending by date
   - Include tournament start date (e.g., "Masters - April 5, 2026")
   - Consider removing redundant "upcoming" tab info

5. **Dashboard tournament display**
   - Too much text/scrolling currently
   - Show only first 5 upcoming tournaments in compact format
   - Separate page for full tournament list if needed

6. **Data refresh indicators**
   - Show last refresh date/time on leagues page for live tournaments
   - Add to teams page as well
   - Include disclaimer about data update frequency

7. **Draft deadline editing**
   - Ability to change draft deadline after league creation

## New Features

8. **Password reset**
   - Send reset email to user
   - Requires email service integration

9. **Permission management**
   - Ability to edit permission levels outside owner portal
   - Prevent lockout scenarios
   - Consider self-service role elevation with safeguards

10. **About page**
    - App description and purpose
    - Data source attribution (Live Golf Data API)
    - Developer info and GitHub link
    - Getting started guide
    - How to create a league
    - Permission levels explained
    - Contact information

11. **Custom domain**
    - Configure custom domain for production

## Future Enhancements

12. **UI revamp**
    - Modernize overall look and feel
    - Brainstorm session needed
    - Consider component library or design system

## Notes

- Items 1-2 are bugs that should be prioritized
- Items 3-7 are quick UX wins
- Items 8-12 require more planning/design
