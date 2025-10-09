"""
Test script to verify live-golf-data API endpoints and document correct usage.
"""
import httpx
import asyncio
import json
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOLF_API_KEY")
BASE_URL = "https://live-golf-data.p.rapidapi.com"

headers = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "live-golf-data.p.rapidapi.com"
}

print(f"API Key: {API_KEY[:15]}...")
print(f"Base URL: {BASE_URL}")
print(f"Headers: {headers}")
print("\n" + "="*80 + "\n")


async def test_endpoint(client, endpoint, params=None, description=""):
    """Test an API endpoint."""
    url = f"{BASE_URL}{endpoint}"
    print(f"\nTesting: {endpoint}")
    print(f"Description: {description}")
    print(f"Full URL: {url}")
    if params:
        print(f"Params: {params}")
    print("-" * 80)
    
    try:
        response = await client.get(url, params=params, timeout=10.0)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ SUCCESS!")
            print(f"Response type: {type(data)}")
            
            if isinstance(data, list):
                print(f"Number of items: {len(data)}")
                if len(data) > 0:
                    print(f"\nFirst item:")
                    print(json.dumps(data[0], indent=2)[:500])
            elif isinstance(data, dict):
                print(f"Keys: {list(data.keys())}")
                print(f"\nSample data:")
                print(json.dumps(data, indent=2)[:500])
            
            return True, data
        else:
            print(f"✗ FAILED")
            print(f"Error: {response.text[:300]}")
            return False, None
            
    except Exception as e:
        print(f"✗ EXCEPTION: {str(e)[:300]}")
        return False, None


async def main():
    """Test various endpoint patterns to find what works."""
    
    async with httpx.AsyncClient(headers=headers) as client:
        
        # Try different common endpoint patterns
        tests = [
            ("/schedule", None, "Get schedule (no params)"),
            ("/schedule", {"tour": "pga"}, "Get PGA schedule"),
            ("/schedule", {"tour": "pga", "year": 2024}, "Get PGA 2024 schedule"),
            ("/schedules", {"year": 2024, "orgId": 1}, "Schedules with orgId"),
            ("/tournament", {"id": "002"}, "Get tournament by ID"),
            ("/tournament", {"tournId": "002", "year": 2024}, "Get tournament (original params)"),
            ("/tournaments", {"tournId": "002", "year": 2024}, "Get tournaments (original params)"),
            ("/leaderboard", None, "Get leaderboard (no params)"),
            ("/leaderboard", {"tournament": "002"}, "Get leaderboard for tournament"),
            ("/organizations", None, "Get organizations"),
            ("/tours", None, "Get tours"),
            ("/players", None, "Get players"),
        ]
        
        successful_endpoints = []
        
        for endpoint, params, description in tests:
            success, data = await test_endpoint(client, endpoint, params, description)
            if success:
                successful_endpoints.append({
                    "endpoint": endpoint,
                    "params": params,
                    "description": description,
                    "sample_data": data
                })
            print("\n")
        
        print("\n" + "="*80)
        print("SUMMARY OF SUCCESSFUL ENDPOINTS")
        print("="*80 + "\n")
        
        if successful_endpoints:
            for item in successful_endpoints:
                print(f"✓ {item['endpoint']}")
                print(f"  Params: {item['params']}")
                print(f"  Description: {item['description']}")
                print()
        else:
            print("✗ No successful endpoints found!")
            print("\nPossible issues:")
            print("1. API key not valid for this API")
            print("2. Need different subscription on RapidAPI")
            print("3. Endpoint structure is different than expected")
            print("\nCheck your RapidAPI dashboard to see which API you're subscribed to")
            print("and what endpoints are available.")


if __name__ == "__main__":
    asyncio.run(main())

