import pandas as pd
import requests
import os
import time

# 🛑 PUT YOUR ACTUAL GEMINI API KEY HERE 🛑
API_KEY = ""

def ask_llm_for_net_score(symbol, combined_text, max_retries=5):
    """Scores a bundle of daily news for a single company with Exponential Backoff."""
    
    prompt = f"""
    You are an elite quantitative hedge fund analyst specializing in the Colombo Stock Exchange.
    You are analyzing ALL the news events that occurred on a single day for the company: {symbol}.
    
    Read the following headlines and summaries. Weigh the positive events against the negative events.
    Determine the NET sentiment impact on the stock price for the upcoming trading weeks.
    
    Score it strictly on a scale from -1.0 to 1.0.
    -1.0 = Extremely Bearish Net Impact
    0.0 = Neutral Net Impact
    1.0 = Extremely Bullish Net Impact
    
    DAILY NEWS DOSSIER FOR {symbol}:
    {combined_text}
    
    OUTPUT INSTRUCTIONS:
    Output ONLY a single float number between -1.0 and 1.0. Do not write any words or explanations.
    """
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    base_wait_time = 5 
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 429:
                wait = base_wait_time * (2 ** attempt) 
                print(f"      ⏳ Rate Limit Hit. Pausing for {wait} seconds...")
                time.sleep(wait)
                continue 
                
            response.raise_for_status() 
            data = response.json()
            score_str = data['candidates'][0]['content']['parts'][0]['text'].strip()
            score = float(score_str)
            
            return max(-1.0, min(1.0, score))
            
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"      ⚠️ API Error (Failed after {max_retries} retries): {e}")
                return 0.0
            else:
                time.sleep(3)

def main():
    base_dir = r"C:\Users\Malith\OneDrive\Desktop\Hedge Fund\AI-Powered-Digital-Hedge-Fund"
    raw_news_file = os.path.join(base_dir, "sp20_alt_news.csv")
    scored_news_file = os.path.join(base_dir, "sp20_alt_news_scored.csv")
    
    print(f"📂 Loading Raw Alternative News from {raw_news_file}...")
    try:
        df_raw = pd.read_csv(raw_news_file)
    except FileNotFoundError:
        print("❌ Could not find the raw alt news dataset. Run alt_news_miner.py first.")
        return

    # Load previously scored days so we don't waste API calls on history
    if os.path.exists(scored_news_file):
        df_scored = pd.read_csv(scored_news_file)
        # Create a set of "Date_Symbol" strings that we have already scored
        already_scored = set(df_scored['Date'] + "_" + df_scored['Symbol'])
    else:
        df_scored = pd.DataFrame(columns=['Date', 'Symbol', 'Alt_News_Sentiment'])
        already_scored = set()

    print("🧠 Awakening the Alt-Data Quant Agent (Aggregator Mode)...")
    
    # Group the raw news by Date and Symbol
    grouped = df_raw.groupby(['Date', 'Symbol'])
    
    new_scores = []

    for (date, symbol), group in grouped:
        # Check if we already scored this exact day for this company
        if f"{date}_{symbol}" in already_scored:
            continue
            
        print(f"\n  📅 Processing {symbol} for Date: {date} ({len(group)} articles found)")
        
        # Combine all articles for this day into one text block
        combined_text = ""
        for i, row in group.iterrows():
            headline = row.get('Headline', 'No Headline')
            summary = row.get('Summary', 'No Summary')
            combined_text += f"--- Article ---\nHeadline: {headline}\nSummary: {summary}\n\n"
            
        score = ask_llm_for_net_score(symbol, combined_text)
        print(f"      🎯 Net AI Sentiment Score: {score}")
        
        new_scores.append({
            'Date': date,
            'Symbol': symbol,
            'Alt_News_Sentiment': score
        })
        
        time.sleep(4) # Standard cruise speed

    # Append new scores to the historical scores database
    if new_scores:
        new_df = pd.DataFrame(new_scores)
        df_scored = pd.concat([df_scored, new_df], ignore_index=True)
        # Sort chronologically
        df_scored = df_scored.sort_values(by=['Date', 'Symbol'], ascending=[False, True])
        df_scored.to_csv(scored_news_file, index=False)
        print(f"\n🎉 Success! Added {len(new_scores)} new daily aggregated scores to the database.")
    else:
        print("\n✅ All historical dates are already scored. No new articles to process.")

if __name__ == "__main__":
    main()