import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import mean_absolute_error
import os

def main():
    file_path = r"C:\Users\Malith\OneDrive\Desktop\Hedge Fund\AI-Powered-Digital-Hedge-Fund\sp20_historical_data.csv"
    print(f"📂 Loading raw historical data from {file_path}...")
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print("❌ Could not find the dataset. Check the path.")
        return

    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(by=['Symbol', 'Date'])

    print("🧮 Calculating Features and 'Target_Price'...")
    
    def prep_regression_data(group):
        # 1. Basic Features
        group['SMA_10'] = group['Close'].rolling(window=10).mean()
        group['SMA_50'] = group['Close'].rolling(window=50).mean()
        
        # 2. THE NEW TARGET: Tomorrow's exact Close Price
        # We shift the Close price backwards by 1 row
        group['Target_Price'] = group['Close'].shift(-1)
        return group

    # Apply math and drop empty rows
    df = df.groupby('Symbol', group_keys=False).apply(prep_regression_data)
    df = df.dropna()

    features = ['Close', 'SMA_10', 'SMA_50', 'Volume']
    X = df[features]
    y = df['Target_Price']

    # Time-Series Split (80% Train, 20% Test)
    split_index = int(len(df) * 0.80)
    
    X_train, X_test = X.iloc[:split_index], X.iloc[split_index:]
    y_train, y_test = y.iloc[:split_index], y.iloc[split_index:]
    
    # 🧠 Initialize the Regressor Brain
    # Notice we are using XGBRegressor now, not XGBClassifier!
    model = xgb.XGBRegressor(
        n_estimators=150,
        learning_rate=0.05,
        max_depth=5,
        random_state=42
    )
    
    print("🧠 Training the Price Prediction Agent. Please wait...")
    model.fit(X_train, y_train)

    # 🔮 Predict exact prices for the unseen test data
    predictions = model.predict(X_test)

    # 📊 Grade the AI
    # We can't use "Accuracy %" for exact numbers. We use Mean Absolute Error (MAE).
    # MAE tells us: "On average, how many Rupees was the AI off by?"
    mae = mean_absolute_error(y_test, predictions)
    
    print("\n==========================================")
    print(f"🎯 AVERAGE ERROR (MAE): Rs. {mae:.2f}")
    print("==========================================\n")
    
    # Let's show a side-by-side comparison of the last 5 days
    print("🔍 Real Price vs. AI Predicted Price (Last 5 Days of Test Data):")
    results = pd.DataFrame({
        'Real Tomorrow Price': y_test.values[-5:],
        'AI Predicted Price': predictions[-5:]
    })
    results['Error'] = abs(results['Real Tomorrow Price'] - results['AI Predicted Price'])
    print(results.round(2).to_string(index=False))

if __name__ == "__main__":
    main()