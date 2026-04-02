import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import urllib.parse # 🚀 NEW: Helps us safely build web URLs

class CSENewsMiner:
    def __init__(self):
        self.base_url = "https://www.cse.lk/api/"
        self.headers = {
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "https://www.cse.lk/"
        }
        self.sp20_map = {
            "JOHN KEELLS HOLDINGS PLC": "JKH.N0000",
            "COMMERCIAL BANK OF CEYLON PLC": "COMB.N0000",
            "LOLC HOLDINGS PLC": "LOLC.N0000",
            "SAMPATH BANK PLC": "SAMP.N0000",
            "HATTON NATIONAL BANK PLC": "HNB.N0000",
            "LANKA IOC PLC": "LIOC.N0000",
            "DIALOG AXIATA PLC": "DIAL.N0000",
            "HAYLEYS PLC": "HAYL.N0000",
            "MELSTACORP PLC": "MELS.N0000",
            "AITKEN SPENCE PLC": "SPEN.N0000",
            "CEYLON TOBACCO COMPANY PLC": "CTC.N0000",
            "CARGILLS (CEYLON) PLC": "CARG.N0000",
            "RICHARD PIERIS AND COMPANY PLC": "RICH.N0000",
            "NATIONAL DEVELOPMENT BANK PLC": "NDB.N0000",
            "LION BREWERY (CEYLON) PLC": "LION.N0000",
            "VALLIBEL ONE PLC": "VONE.N0000",
            "TOKYO CEMENT COMPANY (LANKA) PLC": "TKYO.N0000",
            "DFCC BANK PLC": "DFCC.N0000",
            "KEELLS HOTELS PLC": "KHL.N0000",
            "ACCESS ENGINEERING PLC": "AEL.N0000"
        }

    def fetch_endpoint(self, endpoint):
        try:
            response = requests.post(f"{self.base_url}{endpoint}", headers=self.headers)
            return response.json()
        except Exception:
            return {}

def main():
    miner = CSENewsMiner()
    news_records = []

    print("🕵️‍♂️ Scout Agent: Searching for S&P 20 Corporate News...")

    # --- 1. Fetch General Corporate News ---
    print("📡 Pulling Approved Announcements...")
    app_news = miner.fetch_endpoint("approvedAnnouncement")
    
    if "approvedAnnouncements" in app_news:
        for item in app_news["approvedAnnouncements"]:
            company_name = item.get("company", "").upper()
            
            if company_name in miner.sp20_map:
                try:
                    raw_date = item.get("dateOfAnnouncement")
                    clean_date = datetime.strptime(raw_date, "%d %b %Y").strftime("%Y-%m-%d")
                    
                    category = item.get("announcementCategory", "CORPORATE NEWS")
                    ann_id = item.get("announcementId")
                    
                    # 🚀 YOUR DISCOVERY: Build the exact CSE Web URL
                    if ann_id:
                        safe_category = urllib.parse.quote(category)
                        web_link = f"https://www.cse.lk/general-announcements?id={ann_id}&type={safe_category}"
                    else:
                        web_link = "No Link"

                    news_records.append({
                        "Date": clean_date,
                        "Symbol": miner.sp20_map[company_name],
                        "Headline": category,
                        "PDF_Link": web_link, # We store the web link here!
                        "Source": "General"
                    })
                except Exception:
                    continue

    # --- 2. Fetch Financial News (Earnings, Dividends) ---
    print("📡 Pulling Financial Announcements...")
    fin_news = miner.fetch_endpoint("getFinancialAnnouncement")
    
    if "reqFinancialAnnouncemnets" in fin_news:
        for item in fin_news["reqFinancialAnnouncemnets"]:
            raw_symbol = item.get("symbol", "")
            
            matched_symbol = None
            for sp20_sym in miner.sp20_map.values():
                if sp20_sym.startswith(raw_symbol + "."):
                    matched_symbol = sp20_sym
                    break
            
            if matched_symbol:
                try:
                    raw_date = item.get("uploadedDate").split(" ", 3)
                    date_str = f"{raw_date[0]} {raw_date[1]} {raw_date[2]}"
                    clean_date = datetime.strptime(date_str, "%d %b %Y").strftime("%Y-%m-%d")

                    # Financials usually have the path directly attached
                    pdf_path = item.get("path", "")
                    full_pdf_link = f"https://cdn.cse.lk/{pdf_path}" if pdf_path else "No Link"

                    news_records.append({
                        "Date": clean_date,
                        "Symbol": matched_symbol,
                        "Headline": item.get("fileText", "FINANCIAL REPORT"),
                        "PDF_Link": full_pdf_link,
                        "Source": "Financial"
                    })
                except Exception:
                    continue

    # --- 3. Save to CSV ---
    if news_records:
        new_df = pd.DataFrame(news_records)
        
        save_dir = r"C:\Users\Malith\OneDrive\Desktop\Hedge Fund\AI-Powered-Digital-Hedge-Fund"
        filename = os.path.join(save_dir, "sp20_news_headlines.csv")
        
        if os.path.exists(filename):
            old_df = pd.read_csv(filename)
            df = pd.concat([old_df, new_df])
            df = df.drop_duplicates(subset=["Date", "Symbol", "Headline"], keep="first")
        else:
            df = new_df
            
        df = df.sort_values(by=["Date", "Symbol"], ascending=[False, True])
        
        df.to_csv(filename, index=False)
        print(f"\n🎉 Success! Your database now securely holds {len(df)} historical news items")
        print(f"Dataset saved to: {filename}")
        print("\nPreview of the latest news:")
        print(df[['Date', 'Symbol', 'Headline', 'PDF_Link']].head().to_string(index=False))
    else:
        print("\n⚠️ No recent news found for the S&P 20 companies in the current CSE feed.")

if __name__ == "__main__":
    main()