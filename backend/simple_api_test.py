"""
Live Golf Data API Test Script

Tests all available API endpoints and displays data structure.
Used for API discovery and validation during development.

Run: python backend/simple_api_test.py

Requires: GOLF_API_KEY in .env file
"""
import httpx
import asyncio
import os
from dotenv import load_dotenv

# Step 1: Load environment variables
print("="*80)
print("STEP 1: Loading environment variables")
print("="*80)
load_dotenv()

API_KEY = os.getenv("GOLF_API_KEY")
print(f"API Key found: {API_KEY[:20]}..." if API_KEY else "ERROR: No API key found!")

# Step 2: Set up connection details
print("\n" + "="*80)
print("STEP 2: Setting up connection")
print("="*80)

BASE_URL = "https://live-golf-data.p.rapidapi.com"
print(f"Base URL: {BASE_URL}")

headers = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "live-golf-data.p.rapidapi.com"
}
print(f"Headers configured:")
print(f"  - X-RapidAPI-Key: {API_KEY[:20]}...")
print(f"  - X-RapidAPI-Host: live-golf-data.p.rapidapi.com")


async def test_schedule(year=2024):
    """Test the /schedule endpoint with year parameter."""
    print("\n" + "="*80)
    print(f"STEP 3: Testing /schedule endpoint (year={year})")
    print("="*80)
    
    # Build the full URL
    endpoint = "/schedule"
    params = {"year": year}
    full_url = f"{BASE_URL}{endpoint}"
    
    print(f"Endpoint: {endpoint}")
    print(f"Parameters: {params}")
    print(f"Full URL: {full_url}?year={year}")
    print(f"\nSending request...")
    
    try:
        async with httpx.AsyncClient(headers=headers, timeout=10.0) as client:
            response = await client.get(full_url, params=params)
            
            print(f"\nResponse Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("✓ SUCCESS!")
                data = response.json()
                
                # Show response structure
                if isinstance(data, list):
                    print(f"\nResponse is a LIST with {len(data)} items")
                    if len(data) > 0:
                        print(f"\nFirst tournament:")
                        first = data[0]
                        for key, value in first.items():
                            print(f"  {key}: {value}")
                elif isinstance(data, dict):
                    print(f"\nResponse is a DICT with keys: {list(data.keys())}")
                    for key, value in data.items():
                        print(f"  {key}: {str(value)[:100]}")
                
                return data
            else:
                print(f"✗ FAILED")
                print(f"Error message: {response.text[:500]}")
                return None
                
    except Exception as e:
        print(f"✗ EXCEPTION occurred")
        print(f"Error: {str(e)}")
        return None


async def test_scorecards(tourn_id, year):
    """Test getting scorecards endpoint."""
    print("\n" + "="*80)
    print(f"STEP 4A: Testing /scorecards endpoint")
    print("="*80)
    
    endpoint = "/scorecards"
    params = {"tournId": tourn_id, "year": year}
    full_url = f"{BASE_URL}{endpoint}"
    
    print(f"Endpoint: {endpoint}")
    print(f"Parameters: {params}")
    print(f"Full URL: {full_url}?tournId={tourn_id}&year={year}")
    print(f"\nSending request...")
    
    try:
        async with httpx.AsyncClient(headers=headers, timeout=10.0) as client:
            response = await client.get(full_url, params=params)
            
            print(f"\nResponse Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("✓ SUCCESS!")
                data = response.json()
                
                print(f"\nResponse type: {type(data)}")
                if isinstance(data, dict):
                    print(f"Response keys: {list(data.keys())}")
                    
                    # Check for scorecards
                    scorecards = data.get('scorecards', data.get('players', []))
                    if scorecards:
                        print(f"\nScorecard data has {len(scorecards)} entries")
                        print(f"\nFirst scorecard entry:")
                        first = scorecards[0]
                        for key, val in first.items():
                            print(f"  {key}: {val}")
                
                return data
            else:
                print(f"✗ FAILED - Status {response.status_code}")
                print(f"Error: {response.text[:300]}")
                return None
    except Exception as e:
        print(f"✗ EXCEPTION: {str(e)[:300]}")
        return None


async def test_leaderboard(tourn_id, year, org_id=1):
    """Test getting leaderboard/scores."""
    print("\n" + "="*80)
    print(f"STEP 4B: Testing /leaderboard endpoint for SCORES")
    print("="*80)
    
    endpoint = "/leaderboard"  # SINGULAR, not plural!
    params = {
        "orgId": org_id,      # Required parameter!
        "tournId": tourn_id,
        "year": year
    }
    full_url = f"{BASE_URL}{endpoint}"
    
    print(f"Endpoint: {endpoint}")
    print(f"Parameters: {params}")
    print(f"Full URL: {full_url}?orgId={org_id}&tournId={tourn_id}&year={year}")
    print(f"\nSending request...")
    
    try:
        async with httpx.AsyncClient(headers=headers, timeout=10.0) as client:
            response = await client.get(full_url, params=params)
            
            print(f"\nResponse Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("✓ SUCCESS!")
                data = response.json()
                
                print(f"\n{'='*60}")
                print(f"ALL RESPONSE KEYS:")
                print(f"{'='*60}")
                if isinstance(data, dict):
                    for key in data.keys():
                        print(f"  - {key}")
                else:
                    print(f"Response is type: {type(data)}")
                
                # Show leaderboard structure
                if isinstance(data, dict):
                    # Check for leaderboardRows (the actual player data)
                    leaderboard_rows = data.get('leaderboardRows', [])
                    if leaderboard_rows:
                        print(f"\n✓ Found leaderboardRows with {len(leaderboard_rows)} players!")
                        print(f"\nTop 5 Players:")
                        for i, player in enumerate(leaderboard_rows[:5]):
                            first_name = player.get('firstName', '')
                            last_name = player.get('lastName', '')
                            full_name = f"{first_name} {last_name}".strip()
                            total = player.get('total', 'N/A')
                            position = player.get('position', 'N/A')
                            status = player.get('status', 'N/A')
                            print(f"  {position}. {full_name} - {total} (Status: {status})")
                        
                        print(f"\nFirst player detailed structure:")
                        first = leaderboard_rows[0]
                        print(f"  playerId: {first.get('playerId')}")
                        print(f"  name: {first.get('firstName')} {first.get('lastName')}")
                        print(f"  total: {first.get('total')}")
                        print(f"  position: {first.get('position')}")
                        print(f"  status: {first.get('status')}")
                        print(f"  rounds: {len(first.get('rounds', []))} rounds")
                        if first.get('rounds'):
                            print(f"    Round 1 example: {first['rounds'][0]}")
                    else:
                        print("\n⚠ No leaderboardRows found")
                        print(f"Available keys: {list(data.keys())}")
                
                return data
            else:
                print(f"✗ FAILED - Status {response.status_code}")
                print(f"Error: {response.text[:300]}")
                return None
    except Exception as e:
        print(f"✗ EXCEPTION: {str(e)[:300]}")
        return None


async def test_tournament(tourn_id, year):
    """Test getting tournament details."""
    print("\n" + "="*80)
    print(f"STEP 5: Testing /tournament endpoint (Player Field)")
    print("="*80)
    
    endpoint = "/tournament"
    params = {"tournId": tourn_id, "year": year}  # Fixed: tournId not id
    full_url = f"{BASE_URL}{endpoint}"
    
    print(f"Endpoint: {endpoint}")
    print(f"Parameters: {params}")
    print(f"Full URL: {full_url}?tournId={tourn_id}&year={year}")
    print(f"\nSending request...")
    
    try:
        async with httpx.AsyncClient(headers=headers, timeout=10.0) as client:
            response = await client.get(full_url, params=params)
            
            print(f"\nResponse Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("✓ SUCCESS!")
                data = response.json()
                
                print(f"\nResponse keys: {list(data.keys()) if isinstance(data, dict) else 'LIST'}")
                
                # Check for ANY score-related fields at top level
                print(f"\n{'='*60}")
                print("SEARCHING FOR SCORES IN RESPONSE...")
                print(f"{'='*60}")
                score_fields = ['leaderboard', 'scores', 'results', 'standings', 'finalResults']
                found_scores = {}
                for field in score_fields:
                    if field in data:
                        found_scores[field] = data[field]
                        print(f"✓ Found '{field}' field!")
                
                if found_scores:
                    for field_name, field_data in found_scores.items():
                        print(f"\n{field_name} structure:")
                        if isinstance(field_data, list) and len(field_data) > 0:
                            print(f"  Type: list with {len(field_data)} entries")
                            print(f"  First entry keys: {list(field_data[0].keys()) if isinstance(field_data[0], dict) else 'Not a dict'}")
                            if isinstance(field_data[0], dict):
                                print(f"  First entry sample:")
                                for k, v in list(field_data[0].items())[:5]:
                                    print(f"    {k}: {v}")
                        else:
                            print(f"  Type: {type(field_data)}")
                else:
                    print("✗ No score-related fields found at top level")
                
                # Show tournament details
                if isinstance(data, dict):
                    # Show basic tournament info
                    tourn_info = data.get('tournament', {})
                    if tourn_info:
                        print(f"\nTournament Name: {tourn_info.get('name', 'N/A')}")
                        print(f"Course: {tourn_info.get('course', 'N/A')}")
                        print(f"Purse: {tourn_info.get('purse', 'N/A')}")
                    
                    # Show players
                    players = data.get('players', [])
                    if players:
                        print(f"\n{'='*60}")
                        print(f"PLAYERS IN TOURNAMENT: {len(players)} total")
                        print(f"{'='*60}")
                        
                        # Show structure of first player
                        if len(players) > 0:
                            print(f"\nFirst player structure:")
                            first_player = players[0]
                            print(f"  Type: {type(first_player)}")
                            if isinstance(first_player, dict):
                                print(f"  Keys: {list(first_player.keys())}")
                                for key, val in first_player.items():
                                    print(f"    {key}: {val}")
                            else:
                                print(f"  Value: {first_player}")
                        
                        # Show first 10 players
                        print(f"\nFirst 10 Players:")
                        for i, player in enumerate(players[:10]):
                            if isinstance(player, dict):
                                player_id = player.get('playerId', player.get('id', 'N/A'))
                                first_name = player.get('firstName', '')
                                last_name = player.get('lastName', '')
                                full_name = f"{first_name} {last_name}".strip() or 'N/A'
                                status = player.get('status', 'N/A')
                                
                                # Check for scores
                                total_score = player.get('totalScore', 'N/A')
                                thru = player.get('thru', 'N/A')
                                position = player.get('position', 'N/A')
                                
                                print(f"  {i+1}. {full_name} - Score: {total_score}, Thru: {thru}, Pos: {position}, Status: {status}")
                            else:
                                # Might be just player IDs
                                print(f"  {i+1}. Player ID: {player}")
                        
                        if len(players) > 10:
                            print(f"  ... and {len(players) - 10} more players")
                    else:
                        print("\n⚠ No players found in tournament data")
                
                return data
            else:
                print(f"✗ FAILED - Status {response.status_code}")
                print(f"Error: {response.text[:300]}")
                return None
    except Exception as e:
        print(f"✗ EXCEPTION: {str(e)[:300]}")
        return None


def find_current_or_next_tournament(schedule_data):
    """Find the current or next upcoming tournament."""
    import time
    
    if not schedule_data or not isinstance(schedule_data, dict):
        return None
    
    tournaments = schedule_data.get('schedule', [])
    if not tournaments:
        return None
    
    current_time = int(time.time() * 1000)  # Current time in milliseconds
    
    upcoming_tournaments = []
    
    for tourn in tournaments:
        date_info = tourn.get('date', {})
        start_info = date_info.get('start', {})
        
        # Handle different date formats from API
        if isinstance(start_info, dict) and '$date' in start_info:
            start_date_dict = start_info['$date']
            if isinstance(start_date_dict, dict) and '$numberLong' in start_date_dict:
                start_ms = int(start_date_dict['$numberLong'])
            else:
                start_ms = int(start_date_dict)
        else:
            continue
        
        # Tournament is upcoming if start date is in the future or within last 7 days
        if start_ms >= current_time - (7 * 24 * 60 * 60 * 1000):
            upcoming_tournaments.append({
                'tournament': tourn,
                'start_ms': start_ms
            })
    
    # Sort by start date
    upcoming_tournaments.sort(key=lambda x: x['start_ms'])
    
    if upcoming_tournaments:
        return upcoming_tournaments[0]['tournament']
    
    return None


async def main():
    """Run the tests."""
    # Test 1: Get schedule for 2025 (current year)
    print("\n" + "="*60)
    print("TEST 1: Get 2025 Schedule")
    print("="*60)
    schedule_2025 = await test_schedule(2025)
    
    # Find current/next tournament
    current_tourn = None
    if schedule_2025:
        current_tourn = find_current_or_next_tournament(schedule_2025)
        if current_tourn:
            print("\n" + "="*60)
            print("CURRENT OR NEXT TOURNAMENT")
            print("="*60)
            print(f"Tournament ID: {current_tourn.get('tournId')}")
            print(f"Name: {current_tourn.get('name')}")
            
            date_info = current_tourn.get('date', {})
            start_info = date_info.get('start', {})
            if isinstance(start_info, dict) and '$date' in start_info:
                start_ms = int(start_info['$date']['$numberLong'])
                from datetime import datetime
                start_date = datetime.fromtimestamp(start_ms / 1000)
                print(f"Start Date: {start_date.strftime('%Y-%m-%d')}")
    
    # Test 2: Get schedule for 2024 (for historical data)
    print("\n" + "="*60)
    print("TEST 2: Get 2024 Schedule")
    print("="*60)
    schedule_2024 = await test_schedule(2024)
    
    # Test 3: Get tournament details
    tournament_data = None
    test_tourn = None
    test_year = None
    
    # Test with the tournament from user's example (Valspar Championship)
    # tournId: 475, which we know has leaderboard data
    test_tourn = {'tournId': '475', 'name': 'Valspar Championship'}
    test_year = 2024
    
    if test_tourn:
        tourn_id = test_tourn.get('tournId')
        tourn_name = test_tourn.get('name')
        if tourn_id:
            print("\n" + "="*60)
            print(f"TEST 3: Testing Score Endpoints")
            print(f"Tournament: {tourn_name} (ID: {tourn_id}, Year: {test_year})")
            print("="*60)
            
            # Test leaderboard endpoint (this has the scores!)
            leaderboard_data = await test_leaderboard(tourn_id, test_year, org_id=1)
            
            # Also check tournament endpoint for player field data
            tournament_data = await test_tournament(tourn_id, test_year)
    
    # Summary
    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)
    
    if schedule_2024:
        print("✓ 2024 Schedule works!")
        if isinstance(schedule_2024, dict) and 'schedule' in schedule_2024:
            print(f"  - Found {len(schedule_2024['schedule'])} tournaments")
    
    if schedule_2025:
        print("✓ 2025 Schedule works!")
        if isinstance(schedule_2025, dict) and 'schedule' in schedule_2025:
            print(f"  - Found {len(schedule_2025['schedule'])} tournaments")
    
    if tournament_data:
        print("✓ Tournament detail endpoint works!")
    else:
        print("✗ Tournament detail endpoint not tested")
    
    if not (schedule_2024 or schedule_2025):
        print("\n✗ API connection failed")
        print("\nTroubleshooting:")
        print("1. Check your API key in .env file")
        print("2. Make sure you're subscribed to 'Live Golf Data' on RapidAPI")
        print("3. Verify the endpoint URL is correct")


if __name__ == "__main__":
    asyncio.run(main())

