import requests
import json

class CSENewsScout:
    def __init__(self):
        self.base_url = "https://www.cse.lk/api/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Referer": "https://www.cse.lk/"
        }

    def fetch_news(self, endpoint, payload=None):
        try:
            print(f"\n📡 Pinging endpoint: {endpoint}...")
            response = requests.post(f"{self.base_url}{endpoint}", data=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

def main():
    scout = CSENewsScout()
    
    # 1. Test Approved Announcements (General Corporate News)
    # We send an empty payload to see if it returns a global list of recent news
    approved_news = scout.fetch_news("approvedAnnouncement")
    
    print("\n--- Raw Output: approvedAnnouncement ---")
    if isinstance(approved_news, list):
        print(f"Returns a LIST with {len(approved_news)} items.")
        if len(approved_news) > 0:
            print(json.dumps(approved_news[0], indent=2)) # Print the first announcement
    else:
        print("Returns a DICTIONARY:")
        # Print the first 500 characters so we can see the keys
        print(json.dumps(approved_news, indent=2)[:500])

    # 2. Test Financial Announcements (Earnings, Dividends)
    financial_news = scout.fetch_news("getFinancialAnnouncement")
    
    print("\n--- Raw Output: getFinancialAnnouncement ---")
    if isinstance(financial_news, list):
        print(f"Returns a LIST with {len(financial_news)} items.")
        if len(financial_news) > 0:
            print(json.dumps(financial_news[0], indent=2))
    else:
        print("Returns a DICTIONARY:")
        print(json.dumps(financial_news, indent=2)[:500])

if __name__ == "__main__":
    main()