import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import time
import re
import html

def clean_html(raw_html):
    """Removes HTML tags and decodes weird web characters."""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', str(raw_html))
    return html.unescape(cleantext).upper()

def scrape_external_news():
    print("🌍 Awakening the Alternative Data Miner (WP-REST Engine)...")

    # The hidden WordPress API endpoints for our target sites
    wp_endpoints = [
        "https://economynext.com/wp-json/wp/v2/posts",
        "https://www.lankabusinessonline.com/wp-json/wp/v2/posts",
        "https://bizenglish.adaderana.lk/wp-json/wp/v2/posts"
    ]

    sp20_keywords = {
        "JKH.N0000": ["JOHN KEELLS"],
        "COMB.N0000": ["COMMERCIAL BANK"],
        "LOLC.N0000": ["LOLC HOLDINGS", "LANKA ORIX"], 
        "SAMP.N0000": ["SAMPATH BANK"],
        "HNB.N0000": ["HATTON NATIONAL BANK", "HATTON NATIONAL"],
        "LIOC.N0000": ["LANKA IOC"],
        "DIAL.N0000": ["DIALOG AXIATA"],
        "HAYL.N0000": ["HAYLEYS"],
        "MELS.N0000": ["MELSTACORP"],
        "SPEN.N0000": ["AITKEN SPENCE"],
        "CTC.N0000": ["CEYLON TOBACCO"],
        "CARG.N0000": ["CARGILLS"],
        "RICH.N0000": ["RICHARD PIERIS"],
        "NDB.N0000": ["NATIONAL DEVELOPMENT BANK"],
        "LION.N0000": ["LION BREWERY"],
        "VONE.N0000": ["VALLIBEL ONE"],
        "TKYO.N0000": ["TOKYO CEMENT"],
        "DFCC.N0000": ["DFCC BANK"],
        "KHL.N0000": ["KEELLS HOTELS"],
        "AEL.N0000": ["ACCESS ENGINEERING"]
    }

    base_dir = r"C:\Users\Malith\OneDrive\Desktop\Hedge Fund\AI-Powered-Digital-Hedge-Fund"
    filename = os.path.join(base_dir, "sp20_alt_news.csv")

    # --- THE SMART SWITCH ---
    if os.path.exists(filename):
        print("📂 Existing database found. Fetching only TODAY'S news (Page 1)...")
        pages_to_fetch = 1  # Just top 100 recent articles
    else:
        print("⚠️ No database found! Initiating DEEP ARCHIVE BACKFILL (Last 30 Days)...")
        pages_to_fetch = 5  # 5 pages * 100 articles = 500 historical articles per site!

    records = []
    headers = {"User-Agent": "Mozilla/5.0"}
    thirty_days_ago = datetime.now() - timedelta(days=30)

    for url in wp_endpoints:
        print(f"\n📡 Hacking into {url.split('/')[2]} Archives...")
        
        for page in range(1, pages_to_fetch + 1):
            try:
                # Request up to 100 articles per page
                res = requests.get(f"{url}?per_page=100&page={page}", headers=headers, timeout=10)
                
                if res.status_code != 200:
                    break # Stop if we hit the end of their database
                
                posts = res.json()
                if not posts:
                    break
                
                print(f"  📖 Scanning Page {page} ({len(posts)} articles)...")
                
                for post in posts:
                    # Clean the JSON data
                    headline = clean_html(post.get("title", {}).get("rendered", ""))
                    summary = clean_html(post.get("excerpt", {}).get("rendered", ""))
                    full_text = f"{headline} {summary}"
                    
                    # Parse article date
                    date_str = post.get("date", "").split("T")[0]
                    article_date = datetime.strptime(date_str, "%Y-%m-%d")
                    
                    # Stop processing if the article is older than 30 days
                    if article_date < thirty_days_ago:
                        continue

                    link = post.get("link", "")

                    # Hunt for S&P 20 Mentions
                    for symbol, keywords in sp20_keywords.items():
                        for keyword in keywords:
                            if keyword in full_text:
                                print(f"    🚨 HISTORICAL CATALYST FOUND [{symbol}]: {headline[:50]}...")
                                records.append({
                                    "Date": date_str,
                                    "Symbol": symbol,
                                    "Headline": headline,
                                    "Summary": summary[:200], # Keep it brief for the LLM
                                    "Link": link,
                                    "Source": "Alt_News"
                                })
                                break # Stop checking keywords for this symbol
                
                time.sleep(1) # Be polite to their servers
            except Exception as e:
                print(f"  ⚠️ Error on page {page}: {e}")
                break

    # --- Save to CSV ---
    if records:
        new_df = pd.DataFrame(records)

        if os.path.exists(filename):
            old_df = pd.read_csv(filename)
            df = pd.concat([old_df, new_df])
            # Drop exact duplicates so we don't save the same article twice
            df = df.drop_duplicates(subset=["Link", "Symbol"], keep="first")
        else:
            df = new_df

        df = df.sort_values(by=["Date", "Symbol"], ascending=[False, True])
        df.to_csv(filename, index=False)

        print(f"\n🎉 Success! The Alternative Data Miner saved {len(df)} records.")
        print("\nPreview of the Historical Alternative Data:")
        print(df[['Date', 'Symbol', 'Headline']].head(5).to_string(index=False))
    else:
        print("\n⚠️ No S&P 20 companies mentioned in the archives.")

if __name__ == "__main__":
    scrape_external_news()