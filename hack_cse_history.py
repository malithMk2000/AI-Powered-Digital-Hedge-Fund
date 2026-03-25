import requests
import json

def inspect():
    url = "https://www.cse.lk/api/chartData"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Referer": "https://www.cse.lk/"
    }
    
    # The Golden Payload!
    payload = {"symbol": "ASPI", "chartId": "1", "period": "5"}
    
    print("📡 Pinging CSE for ASPI History...")
    res = requests.post(url, headers=headers, data=payload)
    
    if res.status_code == 200:
        data = res.json()
        print("\n✅ Success! Here is what one day of historical ASPI data looks like:")
        print(json.dumps(data[0], indent=4))
    else:
        print("❌ Failed.")

if __name__ == "__main__":
    inspect()