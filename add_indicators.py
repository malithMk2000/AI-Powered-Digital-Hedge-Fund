import pandas as pd
import os

def main():
    base_dir = r"C:\Users\Malith\OneDrive\Desktop\Hedge Fund\AI-Powered-Digital-Hedge-Fund"
    input_file = os.path.join(base_dir, "sp20_historical_data.csv")
    output_file = os.path.join(base_dir, "sp20_ml_ready.csv")
    
    df = pd.read_csv(input_file)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(by=['Symbol', 'Date'])

    print("🧮 Recalculating Technical Indicators...")
    
    def apply_technical_analysis(group):
        group['SMA_10'] = group['Close'].rolling(window=10).mean()
        group['SMA_50'] = group['Close'].rolling(window=50).mean()
        
        delta = group['Close'].diff()
        gain = delta.clip(lower=0)
        loss = -1 * delta.clip(upper=0)
        ema_gain = gain.ewm(com=13, min_periods=14, adjust=False).mean()
        ema_loss = loss.ewm(com=13, min_periods=14, adjust=False).mean()
        
        rs = ema_gain / ema_loss
        group['RSI_14'] = 100 - (100 / (1 + rs))
        
        ema_12 = group['Close'].ewm(span=12, adjust=False).mean()
        ema_26 = group['Close'].ewm(span=26, adjust=False).mean()
        group['MACD'] = ema_12 - ema_26
        group['MACD_Signal'] = group['MACD'].ewm(span=9, adjust=False).mean()
            
        # We use float so Pandas allows 'NaN' for today's unknown tomorrow
        group['Target_Up'] = (group['Close'].shift(-1) > group['Close']).astype(float)
        # The last row has no "tomorrow", so Target_Up becomes NaN.
        group.loc[group.index[-1], 'Target_Up'] = float('nan')
        
        return group

    df_engineered = df.groupby('Symbol', group_keys=False).apply(apply_technical_analysis)
    
    # Drop rows where SMA_50 is NaN (the first 50 days), but DO NOT drop rows where Target_Up is NaN (Today)
    df_clean = df_engineered.dropna(subset=['SMA_50', 'RSI_14'])

    df_clean.to_csv(output_file, index=False)
    print(f"🎉 ML Dataset ready. Final Row Count: {len(df_clean)}")

if __name__ == "__main__":
    main()