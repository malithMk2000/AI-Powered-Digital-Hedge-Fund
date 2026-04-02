import yfinance as yf
import pandas as pd
import requests
import os
import warnings
from datetime import datetime
warnings.filterwarnings('ignore')

def fetch_cse_aspi_history():
    """Engine 2: Pings the CSE API for 1 Year of historical ASPI data."""
    print("📡 Pinging CSE Servers for 1-Year ASPI History...")
    url = "https://www.cse.lk/api/chartData"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Referer": "https://www.cse.lk/"
    }
    # The Golden Payload!
    payload = {"symbol": "ASPI", "chartId": "1", "period": "5"}
    
    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        data = response.json()
        
        records = []
        if isinstance(data, list) and len(data) > 0:
            for item in data:
                timestamp_ms = item.get("d")
                if timestamp_ms:
                    # Convert 'd' (milliseconds) to YYYY-MM-DD
                    date_str = datetime.fromtimestamp(timestamp_ms / 1000.0).strftime('%Y-%m-%d')
                    records.append({
                        "Date": date_str,
                        "ASPI_Index": item.get("v", 0.0),    # 'v' is the index value
                        "ASPI_Trend_%": item.get("pc", 0.0)  # 'pc' is the percentage change
                    })
        return pd.DataFrame(records)
    except Exception as e:
        print(f"   ⚠️ Could not fetch CSE ASPI history: {e}")
        return pd.DataFrame()

def fetch_macro_data():
    print("🌍 Awakening the Global Macro-Econ Agent...")
    
    # --- ENGINE 1: GLOBAL DATA (Yahoo Finance) ---
    tickers = ["^GSPC", "LKR=X", "BZ=F", "^TNX", "^VIX"]
    print("📡 Downloading global economic data (S&P 500, Oil, USD/LKR, Yields, VIX)...")
    
    # Downloading 1 year to match the CSE data length
    data = yf.download(tickers, period="1y", interval="1d", progress=False)
    
    if isinstance(data.columns, pd.MultiIndex):
        macro_df = data['Close'].reset_index()
    else:
        macro_df = data.reset_index()
        
    macro_df.rename(columns={
        'Date': 'Date',
        '^GSPC': 'Global_Market_Index',
        'LKR=X': 'USD_LKR',
        'BZ=F': 'Brent_Oil',
        '^TNX': 'Global_Interest_Rate',
        '^VIX': 'Global_Fear_Index'
    }, inplace=True)
    
    macro_df['Date'] = pd.to_datetime(macro_df['Date']).dt.strftime('%Y-%m-%d')
    macro_df.ffill(inplace=True)
    macro_df.dropna(inplace=True)
    
    # 🧠 AI Momentum Indicators for Global Data
    macro_df['Global_Market_Trend_%'] = macro_df['Global_Market_Index'].pct_change() * 100
    macro_df['Oil_Trend_%'] = macro_df['Brent_Oil'].pct_change() * 100
    macro_df['Rate_Trend_%'] = macro_df['Global_Interest_Rate'].pct_change() * 100
    macro_df.fillna(0.0, inplace=True)
    
    # --- ENGINE 2: LOCAL DATA (CSE API) ---
    cse_df = fetch_cse_aspi_history()
    
    # --- THE GRAND FUSION ---
    print("🔗 Fusing Global and Local Economies...")
    if not cse_df.empty:
        # Merge the local Sri Lankan data with the global Yahoo data based on the Date
        combined_df = pd.merge(cse_df, macro_df, on='Date', how='left')
    else:
        combined_df = macro_df.copy()
        combined_df['ASPI_Index'] = 0.0
        combined_df['ASPI_Trend_%'] = 0.0

    # Forward fill to handle days where Sri Lankan markets were open but US markets were closed (or vice versa)
    combined_df.ffill(inplace=True)
    combined_df.dropna(inplace=True)

    # Save to the final CSV
    base_dir = r"C:\Users\Malith\OneDrive\Desktop\Hedge Fund\AI-Powered-Digital-Hedge-Fund"
    output_file = os.path.join(base_dir, "global_macro_data.csv")
    combined_df.to_csv(output_file, index=False)
    
    print(f"\n🎉 Success! Global & Local Macro data fused and saved to: {output_file}")
    print("\nPreview of the Macro Environment:")
    
    cols_to_show = ['Date', 'ASPI_Index', 'Global_Market_Index', 'USD_LKR', 'Brent_Oil']
    available_cols = [c for c in cols_to_show if c in combined_df.columns]
    print(combined_df[available_cols].tail(10).to_string(index=False))

if __name__ == "__main__":
    fetch_macro_data()