"""Service for integrating with Live Golf Data API (via RapidAPI)."""
import httpx
import logging
from datetime import date
from typing import List, Dict, Optional
from ..config import settings

logger = logging.getLogger(__name__)


class GolfAPIService:
    """Wrapper for Live Golf Data API (via RapidAPI)."""

    def __init__(self):
        self.base_url = settings.GOLF_API_BASE_URL
        self.api_key = settings.GOLF_API_KEY
        # RapidAPI headers
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "live-golf-data.p.rapidapi.com"
        }
        # API call tracking
        self._call_count = 0
        self._daily_count = 0
        self._current_day = date.today()

    def _track_call(self, endpoint: str, params: dict):
        """Track and log each API call for monitoring."""
        today = date.today()
        if today != self._current_day:
            logger.warning(f"API DAILY SUMMARY: {self._daily_count} calls on {self._current_day}")
            self._daily_count = 0
            self._current_day = today

        self._call_count += 1
        self._daily_count += 1
        logger.warning(
            f"API CALL #{self._call_count} (today: {self._daily_count}) - "
            f"{endpoint} params={params}"
        )

    def get_usage_stats(self) -> dict:
        """Return current API usage statistics."""
        return {
            "total_calls": self._call_count,
            "daily_calls": self._daily_count,
            "current_day": str(self._current_day),
        }

    async def get_schedules(self, year: int) -> List[Dict]:
        """
        Get tournament schedule for a year.

        Args:
            year: Tournament year

        Returns:
            Dict with 'schedule' array containing tournaments
        """
        params = {"year": year}
        self._track_call("/schedule", params)
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/schedule",
                params=params,
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            # Return the schedule array, not the whole response
            return data.get('schedule', [])

    async def get_tournament(self, tourn_id: str, year: int) -> Dict:
        """
        Get detailed tournament information including field (players).

        Args:
            tourn_id: Tournament ID from API (e.g., "016")
            year: Tournament year

        Returns:
            Tournament details with players array at top level
        """
        params = {"tournId": tourn_id, "year": year}
        self._track_call("/tournament", params)
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/tournament",
                params=params,
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    async def get_leaderboard(self, tourn_id: str, year: int, org_id: int = 1) -> Dict:
        """
        Get tournament leaderboard with player scores.

        Args:
            tourn_id: Tournament ID from API
            year: Tournament year
            org_id: Organization ID (1 for PGA Tour)

        Returns:
            Leaderboard data with leaderboardRows containing player scores
        """
        params = {"orgId": org_id, "tournId": tourn_id, "year": year}
        self._track_call("/leaderboard", params)
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/leaderboard",  # SINGULAR!
                params=params,
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    # Note: /scorecards endpoint exists but has 20 requests/day limit on free tier
    # Note: /players search endpoint not tested/confirmed in free tier


# Global service instance
golf_api = GolfAPIService()
