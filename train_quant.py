import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import os
import warnings
warnings.filterwarnings('ignore')

def main():
    base_dir = r"C:\Users\Malith\OneDrive\Desktop\Hedge Fund\AI-Powered-Digital-Hedge-Fund"
    input_file = os.path.join(base_dir, "sp20_ml_ready.csv")

    print(f"📂 Loading ML dataset from {input_file}...")
    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        print("❌ File not found.")
        return

    # 🚀 THE OMNISCIENT AI UPGRADE (FINAL VERSION)
    features = [
        'Close', 'SMA_10', 'SMA_50', 'RSI_14', 'MACD', 'MACD_Signal', 'Volume', # Technicals
        'LLM_Sentiment', 'Alt_News_Sentiment',                                  # Micro & Alt News
        'ASPI_Trend_%', 'Global_Market_Trend_%', 'Oil_Trend_%',                 # Macro Trends
        'Rate_Trend_%', 'USD_LKR', 'Global_Fear_Index'                          # Macro Currency/Rates & VIX
    ]

    target = 'Target_Up'

    # Check if all features exist (graceful fallback if macro miner hasn't updated VIX yet)
    missing_features = [f for f in features if f not in df.columns]
    if missing_features:
        print(f"⚠️ Warning: Missing columns {missing_features}. Filling with 0.0 for now.")
        for col in missing_features:
            df[col] = 0.0

    # Clean the dates and sort chronologically
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(by=['Symbol', 'Date'])
    
    # --- THE BULLETPROOF SPLIT ---
    # Find the absolute latest date in the dataset (Today)
    latest_date = df['Date'].max()
    
    # Everything BEFORE today is used to Train the AI
    train_df = df[df['Date'] < latest_date].copy()
    
    # TODAY's data is strictly used to predict Tomorrow's price action
    live_df = df[df['Date'] == latest_date].copy()

    print(f"🧠 Training the Omniscient Quant Agent on {len(train_df)} historical days...")

    X = train_df[features]
    y = train_df[target]

    # Standard train/test split to test the AI's accuracy on the past
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, shuffle=False)

    model = xgb.XGBClassifier(n_estimators=100, learning_rate=0.1, random_state=42, eval_metric='logloss')
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"🎯 BACKTEST ACCURACY: {acc * 100:.2f}%")

    print("\n=======================================================")
    print("🚀 LIVE TRADING SIGNALS FOR NEXT TRADING DAY 🚀")
    print("=======================================================")

    if len(live_df) == 0:
        print("⚠️ No live data available.")
        return

    # Make predictions for Tomorrow using Today's data
    X_live = live_df[features]
    live_preds = model.predict(X_live)
    live_probs = model.predict_proba(X_live)[:, 1] # Probability of going UP

    live_df['Prediction'] = live_preds
    live_df['Confidence_%'] = (live_probs * 100).round(2)

    # --- THE REGIME FILTER (CRISIS MANAGEMENT) ---
    def apply_crisis_filter(row):
        # If the AI says BUY, but confidence is weak, AND the Global Fear Index is high (> 25)
        if row['Prediction'] == 1 and row['Confidence_%'] < 75.0 and row['Global_Fear_Index'] > 25.0:
            return "🔴 HOLD (OVERRIDDEN DUE TO GLOBAL CRISIS)"
        elif row['Prediction'] == 1:
            return "🟢 BUY / UP"
        else:
            return "🔴 HOLD / DOWN"

    live_df['Signal'] = live_df.apply(apply_crisis_filter, axis=1)

    # Convert date back to string for clean printing
    live_df['Date'] = live_df['Date'].dt.strftime('%Y-%m-%d')

    # Print out the final Master Table
    columns_to_show = ['Symbol', 'Date', 'Close', 'LLM_Sentiment', 'Alt_News_Sentiment', 'Confidence_%', 'Signal']
    print(live_df[columns_to_show].to_string(index=False))
    return live_df[columns_to_show].to_dict(orient='records')

if __name__ == "__main__":
    main()