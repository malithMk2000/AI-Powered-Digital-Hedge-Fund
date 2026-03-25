import requests
import pandas as pd
import time
from datetime import datetime
import os
import warnings
warnings.filterwarnings('ignore') # Hides annoying Pandas warnings

class CSEDataMiner:
    def __init__(self):
        self.base_url = "https://www.cse.lk/api/"
        self.headers = {
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "https://www.cse.lk/"
        }

    def fetch_data(self, endpoint, payload=None):
        try:
            response = requests.post(f"{self.base_url}{endpoint}", data=payload, headers=self.headers)
            return response.json()
        except Exception:
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

    save_dir = r"C:\Users\Malith\OneDrive\Desktop\Hedge Fund\AI-Powered-Digital-Hedge-Fund"
    filename = os.path.join(save_dir, "sp20_historical_data.csv")

    if os.path.exists(filename):
        print("📂 Found existing dataset. Fetching only the latest 1-Week data to update...")
        fetch_period = "2"  # Period 2 = 1 Week (~4 days)
    else:
        print("⚠️ No dataset found. Rebuilding 1-Year historical data from scratch...")
        fetch_period = "5"  # Period 5 = 1 Year (~240 days)

    all_stock_data = []
    print(f"🚀 Pinging CSE for {len(sp20_symbols)} S&P SL 20 companies...\n")

    for symbol in sp20_symbols:
        comp_id = miner.get_company_id(symbol)
        if not comp_id: continue
            
        res = miner.fetch_data("companyChartDataByStock", {"stockId": comp_id, "period": fetch_period})
        if res and "chartData" in res and len(res["chartData"]) > 0:
            for item in res["chartData"]:
                timestamp_ms = item.get("t")
                if not timestamp_ms: continue
                date_obj = datetime.fromtimestamp(timestamp_ms / 1000.0)
                open_price = item.get("o") if item.get("o") is not None else item.get("p")
                
                all_stock_data.append({
                    "Symbol": symbol,
                    "Date": date_obj.strftime('%Y-%m-%d'),
                    "Timestamp": timestamp_ms,
                    "Open": open_price, "High": item.get("h"), "Low": item.get("l"),
                    "Close": item.get("p"), "Volume": item.get("q", 0)
                })
        time.sleep(1) # Be polite to the server

    if all_stock_data:
        # Process the newly fetched data
        new_df = pd.DataFrame(all_stock_data)
        new_df = new_df.sort_values(by=["Symbol", "Timestamp"])
        
        daily_new = new_df.groupby(["Symbol", "Date"]).agg(
            Open=("Open", "first"), High=("High", "max"), Low=("Low", "min"),
            Close=("Close", "last"), Volume=("Volume", "sum")
        ).reset_index()
        
        # Merge with existing data if it exists
        if os.path.exists(filename):
            old_df = pd.read_csv(filename)
            combined_df = pd.concat([old_df, daily_new])
        else:
            combined_df = daily_new
            
        # --- THE FIX: Smart Sorting ---
        # 1. Convert ALL dates (both Excel-broken and standard) to math-based Datetime objects
        # To this (just remove the format parameter!):
        combined_df['Date'] = pd.to_datetime(combined_df['Date'])
        
        # 2. Keep the newest version of the data for any given day
        final_df = combined_df.drop_duplicates(subset=["Symbol", "Date"], keep="last")
        
        # 3. Sort chronologically by Symbol and Date flawlessly
        final_df = final_df.sort_values(by=["Symbol", "Date"])
        
        # 4. Convert back to standard YYYY-MM-DD string format to prevent Excel corruption
        final_df['Date'] = final_df['Date'].dt.strftime('%Y-%m-%d')
            
        # Save the properly ordered CSV
        final_df.to_csv(filename, index=False)
        print(f"🎉 Success! Dataset seamlessly updated and chronologically sorted. Total Rows: {len(final_df)}")
    else:
        print("⚠️ Failed to pull new data. Check your internet connection or CSE API status.")

if __name__ == "__main__":
    main()