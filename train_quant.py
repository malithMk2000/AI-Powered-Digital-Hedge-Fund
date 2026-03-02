import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import accuracy_score, classification_report
import warnings
warnings.filterwarnings('ignore') # Hides annoying Pandas copy warnings

def main():
    file_path = r"C:\Users\Malith\OneDrive\Desktop\Hedge Fund\AI-Powered-Digital-Hedge-Fund\sp20_ml_ready.csv"
    print(f"📂 Loading ML dataset from {file_path}...")
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print("❌ Could not find the dataset. Check the path.")
        return

    # Ensure chronological order
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(by=['Symbol', 'Date'])

    features = ['Close', 'SMA_10', 'SMA_50', 'RSI_14', 'MACD', 'MACD_Signal', 'Volume']
    
    # 🚀 THE UPGRADE: SMART SEPARATION
    # We find the rows where 'Target_Up' is blank (NaN). These are our Live Data rows for tomorrow!
    live_data = df[df['Target_Up'].isna()].copy()
    
    # Everything else (where Target_Up has a 0.0 or 1.0) is historical data for training
    historical_data = df[df['Target_Up'].notna()].copy()

    if len(historical_data) == 0:
        print("⚠️ Not enough historical data to train the model.")
        return

    X_hist = historical_data[features]
    y_hist = historical_data['Target_Up']

    # 80/20 Time-Series Split for evaluation
    split_index = int(len(historical_data) * 0.80)
    
    X_train, X_test = X_hist.iloc[:split_index], X_hist.iloc[split_index:]
    y_train, y_test = y_hist.iloc[:split_index], y_hist.iloc[split_index:]
    
    count_class_0 = len(y_train[y_train == 0])
    count_class_1 = len(y_train[y_train == 1])
    bravery_weight = count_class_0 / count_class_1 if count_class_1 > 0 else 1.0

    model = xgb.XGBClassifier(
        n_estimators=150, 
        learning_rate=0.05, 
        max_depth=5, 
        random_state=42,
        scale_pos_weight=bravery_weight, 
        eval_metric='logloss'
    )
    
    print(f"🧠 Training the Quant Agent on {len(X_train)} historical days...")
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    print(f"🎯 BACKTEST ACCURACY: {accuracy * 100:.2f}%")

    # --- LIVE TRADING SIGNALS ---
    print("\n=======================================================")
    print("🚀 LIVE TRADING SIGNALS FOR NEXT TRADING DAY 🚀")
    print("=======================================================\n")
    
    if len(live_data) > 0:
        # We feed the features from the live data (the blank target days) into the trained AI
        X_live = live_data[features]
        live_predictions = model.predict(X_live)
        
        # Attach predictions to our live data dataframe
        live_data['Signal'] = live_predictions
        live_data['Prediction'] = live_data['Signal'].map({1: "🟢 BUY / UP", 0: "🔴 HOLD / DOWN"})
        
        # Clean up the output table for the Hedge Fund manager (You!)
        trade_desk = live_data[['Symbol', 'Date', 'Close', 'RSI_14', 'Prediction']].copy()
        trade_desk['Date'] = trade_desk['Date'].dt.strftime('%Y-%m-%d')
        trade_desk.rename(columns={'Date': 'Data Date (Last Close)'}, inplace=True)
        
        print(trade_desk.to_string(index=False))
    else:
        print("⚠️ No live data found. Ensure add_indicators.py leaves the last day's Target_Up blank.")

if __name__ == "__main__":
    main()