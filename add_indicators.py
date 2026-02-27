import pandas as pd
import os

def main():
    # Updated paths based on your new directory
    base_dir = r"C:\Users\Malith\OneDrive\Desktop\Hedge Fund\AI-Powered-Digital-Hedge-Fund"
    input_file = os.path.join(base_dir, "sp20_historical_data.csv")
    output_file = os.path.join(base_dir, "sp20_ml_ready.csv")
    
    print(f"📂 Loading raw daily data from {input_file}...")
    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        print(f"❌ Could not find the input CSV. Please ensure the file is at: {input_file}")
        return

    # Ensure Date is recognized as a time object and sorted perfectly
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(by=['Symbol', 'Date'])

    print("🧮 Calculating Technical Indicators using pure Pandas...")
    
    def apply_technical_analysis(group):
        # 1. Simple Moving Averages (Trend)
        group['SMA_10'] = group['Close'].rolling(window=10).mean()
        group['SMA_50'] = group['Close'].rolling(window=50).mean()
        
        # 2. Relative Strength Index (RSI - 14 day)
        delta = group['Close'].diff()
        gain = delta.clip(lower=0)
        loss = -1 * delta.clip(upper=0)
        
        # Exponential moving average for RSI
        ema_gain = gain.ewm(com=13, min_periods=14, adjust=False).mean()
        ema_loss = loss.ewm(com=13, min_periods=14, adjust=False).mean()
        
        rs = ema_gain / ema_loss
        group['RSI_14'] = 100 - (100 / (1 + rs))
        
        # 3. MACD (Trend-following momentum)
        ema_12 = group['Close'].ewm(span=12, adjust=False).mean()
        ema_26 = group['Close'].ewm(span=26, adjust=False).mean()
        group['MACD'] = ema_12 - ema_26
        group['MACD_Signal'] = group['MACD'].ewm(span=9, adjust=False).mean()
            
        # 4. THE TARGET VARIABLE (The Answer Key for our AI)
        # Shift the close price backwards by 1 to get "Tomorrow's Price"
        # If Tomorrow's Price > Today's Price, Target = 1 (Buy/Up). Else = 0 (Sell/Down).
        group['Target_Up'] = (group['Close'].shift(-1) > group['Close']).astype(int)
        
        return group

    # Apply the math to the grouped dataframe
    df_engineered = df.groupby('Symbol', group_keys=False).apply(apply_technical_analysis)
    
    # Clean up: Drop rows with NaN (like the first 50 days that can't have a 50-day average)
    df_clean = df_engineered.dropna()

    # Save the final ML-ready dataset
    df_clean.to_csv(output_file, index=False)
    
    print(f"\n🎉 Success! ML Dataset saved to: {output_file}")
    print(f"Total rows ready for AI training: {len(df_clean)}")
    
    print("\nPreview of ML Features:")
    cols_to_show = ['Symbol', 'Date', 'Close', 'RSI_14', 'SMA_50', 'Target_Up']
    print(df_clean[cols_to_show].head(7))

if __name__ == "__main__":
    main()