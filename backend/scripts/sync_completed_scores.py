"""
Script to sync scores for completed tournaments.
This will fetch leaderboard data from the Golf API and update player scores.
"""

import urllib.request
import json
import os
from datetime import datetime

BASE_URL = "http://localhost:8000/api/tournaments"

def call_api(url, method="GET", data=None, headers=None):
    """Make HTTP request using urllib."""
    req = urllib.request.Request(url, method=method)
    if headers:
        for key, value in headers.items():
            req.add_header(key, value)
    if data:
        req.add_header('Content-Type', 'application/json')
        data = json.dumps(data).encode('utf-8')
    
    try:
        with urllib.request.urlopen(req, data=data) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"HTTP Error: {e.code} - {error_body}")
        raise
    except Exception as e:
        print(f"Network Error: {e}")
        raise

def sync_scores():
    """Sync scores for all completed tournaments."""
    print("=" * 60)
    print("Syncing Scores for Completed Tournaments")
    print("=" * 60)

    # Step 1: Get all tournaments
    print("\n[1] Fetching tournaments from database...")
    try:
        tournaments = call_api(BASE_URL)
        print(f"[OK] Found {len(tournaments)} tournaments")
    except Exception as e:
        print(f"[ERROR] Failed to get tournaments: {e}")
        return

    # Step 2: Filter completed tournaments
    print("\n[2] Identifying completed tournaments...")
    completed = []
    today = datetime.now()
    
    for t in tournaments:
        end_date_str = t.get('end_date')
        if end_date_str:
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
            if end_date < today:
                completed.append(t)
                print(f"  - {t['name']} (ended {end_date_str})")
    
    if not completed:
        print("[INFO] No completed tournaments found")
        return
    
    print(f"\n[OK] Found {len(completed)} completed tournament(s) to sync")

    # Step 3: Sync scores for each completed tournament
    print("\n[3] Syncing scores...")
    synced = 0
    errors = 0

    for t in completed:
        tournament_id = t['id']
        name = t['name']
        print(f"\n  {name} (ID: {tournament_id})... ", end="")
        try:
            result = call_api(f"{BASE_URL}/{tournament_id}/sync-scores", method="POST")
            print("[OK]")
            synced += 1
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print("[SKIP] Scores not available in API")
            else:
                error_detail = json.loads(e.read().decode('utf-8')).get('detail', 'Unknown error')
                print(f"[ERROR] {e.code}: {error_detail}")
                errors += 1
        except Exception as e:
            print(f"[ERROR] Exception: {e}")
            errors += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("Sync Summary")
    print("=" * 60)
    print(f"  Synced: {synced}")
    print(f"  Errors: {errors}")
    print(f"  Total: {len(completed)}")
    print("\n[DONE] Score sync complete!")

if __name__ == "__main__":
    sync_scores()

