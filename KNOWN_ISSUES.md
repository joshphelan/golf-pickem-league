# Known Issues

**Last Updated**: January 22, 2026

## Current Limitations

### Golf API Player Data Timing
The Golf API doesn't populate player rosters until about a week before tournaments start. This is handled automatically by Job #2 (Player Refresh), which runs every Friday and refreshes players for upcoming tournaments. No manual action needed.

## Production Status

Application is production-ready:
- All 4 background jobs working (tournament import, player refresh, score sync, backups)
- Full user flow tested and functional
- Database schema finalized
- Authentication and permissions complete

Ready to deploy using Railway. See `DEPLOYMENT_GUIDE.md`.
