import requests
import pandas as pd
import time
from datetime import datetime
import os

class CSEDataMiner:
    def __init__(self):
        self.base_url = "https://www.cse.lk/api/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Referer": "https://www.cse.lk/"
        }

    def fetch_data(self, endpoint, payload=None):
        try:
            response = requests.post(f"{self.base_url}{endpoint}", data=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return None

    def get_company_id(self, symbol):
        data = self.fetch_data("companyInfoSummery", {"symbol": symbol})
        if data and "reqSymbolInfo" in data:
            return data["reqSymbolInfo"].get("id")
        return None

def main():
    miner = CSEDataMiner()
    
    sp20_symbols = [
        "JKH.N0000", "COMB.N0000", "LOLC.N0000", "SAMP.N0000", "HNB.N0000",
        "LIOC.N0000", "DIAL.N0000", "HAYL.N0000", "MELS.N0000", "SPEN.N0000",
        "CTC.N0000", "CARG.N0000", "RICH.N0000", "NDB.N0000", "LION.N0000",
        "VONE.N0000", "TKYO.N0000", "DFCC.N0000", "KHL.N0000", "AEL.N0000"
    ]

    all_stock_data = []
    print(f"🚀 Starting Historical Extraction for {len(sp20_symbols)} S&P SL 20 companies...")
    print("Fetching 1 Year of Data (Period='5')...\n")

    for symbol in sp20_symbols:
        print(f"Processing {symbol}...", end=" ")
        
        comp_id = miner.get_company_id(symbol)
        if not comp_id:
            print("❌ Failed to get ID.")
            continue
            
        # Using period="5" which maps to approx 1 year of daily charts
        res = miner.fetch_data("companyChartDataByStock", {"stockId": comp_id, "period": "5"})
        
        if res and "chartData" in res and len(res["chartData"]) > 0:
            records = res["chartData"]
            
            for item in records:
                timestamp_ms = item.get("t")
                if not timestamp_ms: continue
                    
                date_obj = datetime.fromtimestamp(timestamp_ms / 1000.0)
                open_price = item.get("o") if item.get("o") is not None else item.get("p")
                
                all_stock_data.append({
                    "Symbol": symbol,
                    "Date": date_obj.strftime('%Y-%m-%d'),
                    "Timestamp": timestamp_ms, # Keep exact time for accurate Open/Close aggregation
                    "Open": open_price,
                    "High": item.get("h"),
                    "Low": item.get("l"),
                    "Close": item.get("p"),
                    "Volume": item.get("q", 0)
                })
            print(f"✅ Extracted raw records.")
        else:
            print("❌ No chart data.")
            
        time.sleep(1)

    if all_stock_data:
        # Convert to Pandas
        df = pd.DataFrame(all_stock_data)
        
        # 1. Sort by Exact Time so the First/Last logic works correctly
        df = df.sort_values(by=["Symbol", "Timestamp"])
        
        # 2. Aggregate Intraday into True Daily OHLCV
        print("\n🗜️ Aggregating data into Daily summaries...")
        daily_df = df.groupby(["Symbol", "Date"]).agg(
            Open=("Open", "first"),
            High=("High", "max"),
            Low=("Low", "min"),
            Close=("Close", "last"),
            Volume=("Volume", "sum")
        ).reset_index()
        
        save_directory = r"C:\Users\Malith\OneDrive\Desktop\Hedge Fund\AI-Powered-Digital-Hedge-Fund"
        filename = os.path.join(save_directory, "sp20_historical_data.csv")
        os.makedirs(save_directory, exist_ok=True)
        
        daily_df.to_csv(filename, index=False)
        print(f"🎉 Success! Dataset saved to: {filename}")
        print(f"Total Daily Rows: {len(daily_df)}")
        print("\nPreview:")
        print(daily_df.head())
    else:
        print("\n⚠️ No data extracted.")

if __name__ == "__main__":
    main()