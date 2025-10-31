"""
Import first 5 and last 5 tournaments from 2025 PGA Tour schedule.
This is a one-time/manual script for testing and initial setup.

Production: The scheduler will handle automatic tournament imports.
"""
import asyncio
import sys
import urllib.request
import urllib.error
import json
from pathlib import Path

# Add parent directory to path to import from app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.golf_api_service import golf_api

BASE_URL = "http://localhost:8000/api/tournaments"


def call_backend_import(tourn_id: str, year: int):
    """Call backend import endpoint."""
    data = json.dumps({"tourn_id": tourn_id, "year": year}).encode('utf-8')
    req = urllib.request.Request(
        f"{BASE_URL}/import",
        data=data,
        method="POST"
    )
    req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8')


async def main():
    print("=" * 60)
    print("Importing 2025 PGA Tour Tournaments")
    print("=" * 60)
    
    # Step 1: Get 2025 schedule from Golf API
    print("\n[1] Fetching 2025 schedule from Golf API...")
    try:
        schedule_data = await golf_api.get_schedules(2025)
        print(f"[OK] Found {len(schedule_data)} tournaments")
    except Exception as e:
        print(f"[ERROR] Failed to fetch schedule: {e}")
        return
    
    # Step 2: Parse and sort tournaments
    print("\n[2] Parsing tournament data...")
    tournaments = []
    for t in schedule_data:
        tourn_id = str(t.get('tournId', ''))
        name = t.get('name', '')
        
        # Parse date
        date_obj = t.get('date', {})
        start_date = None
        if isinstance(date_obj, dict):
            start_obj = date_obj.get('start', {})
            if isinstance(start_obj, dict):
                timestamp = start_obj.get('$date', {}).get('$numberLong')
                if timestamp:
                    from datetime import datetime
                    start_date = datetime.fromtimestamp(int(timestamp) / 1000).date()
        
        if tourn_id and name and start_date:
            tournaments.append({
                'tournId': tourn_id,
                'name': name,
                'start_date': start_date,
                'year': 2025
            })
    
    print(f"[OK] Parsed {len(tournaments)} valid tournaments")
    
    # Step 3: Sort and select first 5 + last 5
    tournaments_sorted = sorted(tournaments, key=lambda t: t['start_date'])
    to_import = tournaments_sorted[:5] + tournaments_sorted[-5:]
    
    print(f"\n[3] Selected {len(to_import)} tournaments to import:")
    print("\nFirst 5 (earliest):")
    for t in tournaments_sorted[:5]:
        print(f"  - {t['name']} ({t['start_date']})")
    print("\nLast 5 (latest):")
    for t in tournaments_sorted[-5:]:
        print(f"  - {t['name']} ({t['start_date']})")
    
    # Step 4: Import each tournament via backend
    print(f"\n[4] Importing tournaments via backend API...")
    imported = 0
    skipped = 0
    errors = 0
    
    for tournament in to_import:
        name = tournament['name']
        tourn_id = tournament['tournId']
        year = tournament['year']
        
        print(f"\n  {name} (ID: {tourn_id})...", end=" ")
        
        status, response = call_backend_import(tourn_id, year)
        
        if status == 201:
            print("[OK]")
            imported += 1
        elif status == 400 and "already exists" in str(response):
            print("[SKIP - already exists]")
            skipped += 1
        else:
            print(f"[ERROR {status}]")
            print(f"    {str(response)[:200]}")
            errors += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("Import Summary")
    print("=" * 60)
    print(f"  Imported: {imported}")
    print(f"  Skipped: {skipped}")
    print(f"  Errors: {errors}")
    print(f"  Total: {len(to_import)}")
    print("\n[DONE] Tournaments ready for league creation!")


if __name__ == "__main__":
    asyncio.run(main())

