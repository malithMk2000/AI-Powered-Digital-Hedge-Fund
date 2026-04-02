import pandas as pd
import requests
import PyPDF2
import io
import os
import time

# 🛑 PUT YOUR GEMINI API KEY HERE 🛑
API_KEY = ""

def extract_text_from_pdf(url):
    """Downloads the PDF and extracts the first 5 pages of text for the LLM."""
    if url == "No Link" or pd.isna(url) or not str(url).startswith("http"):
        return ""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        pdf_file = io.BytesIO(response.content)
        reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        num_pages = min(5, len(reader.pages))
        for i in range(num_pages):
            page_text = reader.pages[i].extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception:
        return ""

def ask_llm_for_score(headline, pdf_text, max_retries=5):
    """Feeds the text DIRECTLY to Google's Raw API with Smart Retries."""
    if not pdf_text:
        content_to_analyze = f"Headline: {headline}"
    else:
        content_to_analyze = f"Headline: {headline}\n\nDocument Extract:\n{pdf_text[:10000]}"

    prompt = f"""
    You are an elite quantitative hedge fund analyst specializing in the Colombo Stock Exchange (CSE).
    Analyze the following corporate announcement and/or financial document extract.
    
    Determine the sentiment impact on the stock price for the next trading day.
    Score it strictly on a scale from -1.0 to 1.0.
    -1.0 = Extremely Bearish (Sell immediately, massive losses, default, watch list)
    0.0 = Neutral (Routine disclosure, no major price impact expected)
    1.0 = Extremely Bullish (Record profits, massive dividends, major acquisitions)
    
    Data to analyze:
    {content_to_analyze}
    
    OUTPUT INSTRUCTIONS:
    You must output ONLY a single float number between -1.0 and 1.0. Do not write any words, explanations, or formatting. Just the number.
    """
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    base_wait_time = 5 
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 429:
                wait = base_wait_time * (2 ** attempt)
                print(f"      ⏳ Rate Limit Hit (429). Pausing for {wait} seconds...")
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
    input_file = os.path.join(base_dir, "sp20_news_headlines.csv")
    
    print(f"📂 Loading News Desk from {input_file}...")
    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        print("❌ Could not find the news dataset.")
        return

    print("🧠 Awakening the LLM Quant Agent (Direct API Mode)...")
    
    # 🚀 THE FIX: Only initialize the column with NA if it doesn't exist yet
    if 'LLM_Sentiment' not in df.columns:
        df['LLM_Sentiment'] = pd.NA
    
    for index, row in df.iterrows():
        # 🚀 THE SHIELD: Check if the score is blank (NaN) before doing ANY work
        if pd.isna(row['LLM_Sentiment']) or row['LLM_Sentiment'] == "":
            headline = row['Headline']
            symbol = row['Symbol']
            url = row.get('PDF_Link', "")
            
            print(f"  📖 LLM is reading {symbol} -> {headline[:30]}...")
            
            pdf_text = extract_text_from_pdf(url) if str(url).startswith("http") else ""
            
            score = ask_llm_for_score(headline, pdf_text)
            df.at[index, 'LLM_Sentiment'] = score
            
            print(f"      🎯 LLM Score: {score}")
            
            # 5-second pause to respect API limits
            time.sleep(5)

    # Save the updated scores
    df.to_csv(input_file, index=False)
    
    print("\n🎉 Success! The LLM has finished reading and scoring the new disclosures.")
    
    # Safely display movers by making sure we don't trip over NaNs
    movers = df[pd.notna(df['LLM_Sentiment'])]
    movers = movers[movers['LLM_Sentiment'] != 0.0]
    
    print("\n🔥 LLM IDENTIFIED MARKET CATALYSTS:")
    print(movers[['Date', 'Symbol', 'Headline', 'LLM_Sentiment']].head(10).to_string(index=False))

if __name__ == "__main__":
    main()