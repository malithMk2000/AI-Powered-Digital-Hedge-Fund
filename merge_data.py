import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

def main():
    base_dir = r"C:\Users\Malith\OneDrive\Desktop\Hedge Fund\AI-Powered-Digital-Hedge-Fund"
    ml_file = os.path.join(base_dir, "sp20_ml_ready.csv")
    news_file = os.path.join(base_dir, "sp20_news_headlines.csv")

    print("📂 Loading Mathematical Data...")
    try:
        df_ml = pd.read_csv(ml_file)
    except FileNotFoundError:
        print(f"❌ Could not find {ml_file}")
        return

    print("📂 Loading LLM Sentiment Data...")
    try:
        df_news = pd.read_csv(news_file)
    except FileNotFoundError:
        print(f"❌ Could not find {news_file}")
        return

    # Ensure dates align perfectly
    df_ml['Date'] = pd.to_datetime(df_ml['Date']).dt.strftime('%Y-%m-%d')
    df_news['Date'] = pd.to_datetime(df_news['Date']).dt.strftime('%Y-%m-%d')

    if 'LLM_Sentiment' not in df_news.columns:
        print("❌ No 'LLM_Sentiment' found. Please run llm_scorer.py first!")
        return

    print("🧮 Aggregating daily LLM news scores...")
    # If a company has 2 announcements on the same day (like NDB's two dividends), we average the score
    daily_sentiment = df_news.groupby(['Date', 'Symbol'])['LLM_Sentiment'].mean().reset_index()

    print("🔗 Fusing Mathematics with AI Market Sentiment...")
    # Clean up any old sentiment columns so we don't get duplicates
    if 'LLM_Sentiment' in df_ml.columns:
        df_ml = df_ml.drop(columns=['LLM_Sentiment'])
    if 'Sentiment_Score' in df_ml.columns:
        df_ml = df_ml.drop(columns=['Sentiment_Score'])

    # Left join: Keep all ML rows, attach news if it exists for that day
    df_merged = pd.merge(df_ml, daily_sentiment, on=['Date', 'Symbol'], how='left')

    # If there was no news that day, the score is 0.0 (Neutral)
    df_merged['LLM_Sentiment'] = df_merged['LLM_Sentiment'].fillna(0.0)

    # Save the upgraded dataset back to the ml_ready file
    df_merged.to_csv(ml_file, index=False)

    print(f"🎉 Success! The Grand Merge is complete.")
    
    # Show a preview of days where actual news happened
    movers = df_merged[df_merged['LLM_Sentiment'] != 0.0]
    if len(movers) > 0:
        print("\n🔥 PREVIEW OF AI-ENHANCED ML DATASET (These rows have active news):")
        cols_to_print = [c for c in ['Date', 'Symbol', 'Close', 'RSI_14', 'LLM_Sentiment', 'Target_Up'] if c in df_merged.columns]
        print(movers[cols_to_print].head(10).to_string(index=False))
    else:
        print("\n⚠️ Merge successful, but no non-zero sentiment scores overlapped with your ML trading days.")

if __name__ == "__main__":
    main()