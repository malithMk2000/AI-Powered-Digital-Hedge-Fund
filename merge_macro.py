import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

def main():
    base_dir = r"C:\Users\Malith\OneDrive\Desktop\Hedge Fund\AI-Powered-Digital-Hedge-Fund"
    ml_file = os.path.join(base_dir, "sp20_ml_ready.csv")
    macro_file = os.path.join(base_dir, "global_macro_data.csv")

    print("📂 Loading Micro-Econ Data (Technicals + News)...")
    try:
        df_ml = pd.read_csv(ml_file)
    except FileNotFoundError:
        print(f"❌ Could not find {ml_file}")
        return

    print("🌍 Loading Macro-Econ Data (Global + ASPI)...")
    try:
        df_macro = pd.read_csv(macro_file)
    except FileNotFoundError:
        print(f"❌ Could not find {macro_file}")
        return

    # Ensure dates align perfectly
    df_ml['Date'] = pd.to_datetime(df_ml['Date']).dt.strftime('%Y-%m-%d')
    df_macro['Date'] = pd.to_datetime(df_macro['Date']).dt.strftime('%Y-%m-%d')


    # =========================================================================
    # 🚀 NEW: Load the Pre-Scored Alternative News Data (INSERTED HERE)
    # =========================================================================
    print("📰 Loading Alternative News Data...")
    alt_news_file = os.path.join(base_dir, "sp20_alt_news_scored.csv") 
    
    # Drop Alt_News_Sentiment if it already exists so we can update it cleanly
    if 'Alt_News_Sentiment' in df_ml.columns:
        df_ml = df_ml.drop(columns=['Alt_News_Sentiment'])
    
    if os.path.exists(alt_news_file):
        df_alt = pd.read_csv(alt_news_file)
        # Because alt_news_scorer.py already grouped them by day, we just do a direct merge!
        df_ml = pd.merge(df_ml, df_alt[['Date', 'Symbol', 'Alt_News_Sentiment']], on=['Date', 'Symbol'], how='left')
        df_ml['Alt_News_Sentiment'] = df_ml['Alt_News_Sentiment'].fillna(0.0)
    else:
        df_ml['Alt_News_Sentiment'] = 0.0
    # =========================================================================

    print("🔗 Fusing Macro Environment with Micro Stock Data...")
    
    # Drop macro columns if they already exist so we don't get duplicates if you run it twice
    macro_cols_to_drop = [col for col in df_macro.columns if col in df_ml.columns and col != 'Date']
    df_ml = df_ml.drop(columns=macro_cols_to_drop, errors='ignore')

    # Left join: Match the macro data to every single stock row based on the Date
    df_merged = pd.merge(df_ml, df_macro, on='Date', how='left')

    # If any macro data is missing for a specific day (e.g. US market closed), carry forward the last known global value
    df_merged.ffill(inplace=True)
    df_merged.fillna(0.0, inplace=True) # Catch any remaining NaNs at the very top

    # Save the ultimate dataset back to the ml_ready file
    df_merged.to_csv(ml_file, index=False)

    print(f"🎉 Success! The Ultimate Merge is complete. Total Rows: {len(df_merged)}")
    print("\n🔥 PREVIEW OF THE OMNISCIENT AI DATASET:")
    
    cols_to_print = ['Date', 'Symbol', 'Close', 'RSI_14', 'LLM_Sentiment', 'ASPI_Trend_%', 'Global_Market_Trend_%']
    available_cols = [c for c in cols_to_print if c in df_merged.columns]
    print(df_merged[available_cols].tail(10).to_string(index=False))

if __name__ == "__main__":
    main()