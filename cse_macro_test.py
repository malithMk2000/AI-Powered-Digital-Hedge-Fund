import requests
import json

def test_cse_macro():
    base_url = "https://www.cse.lk/api/"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Referer": "https://www.cse.lk/"
    }

    print("📡 Pinging CSE /api/aspiData...")
    try:
        response = requests.post(f"{base_url}aspiData", headers=headers)
        response.raise_for_status()
        data = response.json()
        
        print("\n✅ Success! Here is the raw ASPI data:")
        # We slice it if it's a huge list, just to see the structure
        if isinstance(data, list):
             print(json.dumps(data[:2], indent=2))
             print(f"... (and {len(data) - 2} more items)")
        else:
             print(json.dumps(data, indent=2))
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_cse_macro()