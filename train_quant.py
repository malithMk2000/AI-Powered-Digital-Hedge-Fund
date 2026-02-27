import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import accuracy_score, classification_report
import os

def main():
    # 1. Load the ML-ready data
    file_path = r"C:\Users\Malith\OneDrive\Desktop\Hedge Fund\AI-Powered-Digital-Hedge-Fund\sp20_ml_ready.csv"
    print(f"📂 Loading ML dataset from {file_path}...")
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print("❌ Could not find the dataset. Check the path.")
        return

    # Ensure data is sorted by Date (Crucial for Time-Series!)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(by='Date')

    # 2. Define our Features (X) and our Target (y)
    # These are the columns the AI is allowed to look at
    features = ['Close', 'SMA_10', 'SMA_50', 'RSI_14', 'MACD', 'MACD_Signal']
    
    X = df[features]
    y = df['Target_Up']

    # 3. Time-Series Split (80% Training, 20% Testing)
    # We CANNOT randomly shuffle stock data, because you can't use tomorrow's data to predict today!
    split_index = int(len(df) * 0.80)
    
    X_train, X_test = X.iloc[:split_index], X.iloc[split_index:]
    y_train, y_test = y.iloc[:split_index], y.iloc[split_index:]
    
    print(f"📈 Training on {len(X_train)} historical days...")
    print(f"🔮 Testing (Predicting) on {len(X_test)} unseen future days...\n")

    # 4. Initialize and Train the XGBoost Brain
    # learning_rate and max_depth act as the "hyperparameters" (the settings of the brain)
    model = xgb.XGBClassifier(
        n_estimators=100, 
        learning_rate=0.05, 
        max_depth=4, 
        random_state=42,
        eval_metric='logloss'
    )
    
    print("🧠 Training the Quant Agent. Please wait...")
    model.fit(X_train, y_train)

    # 5. Make Predictions on the Test Set
    predictions = model.predict(X_test)

    # 6. Grade the AI's Performance
    accuracy = accuracy_score(y_test, predictions)
    print("==========================================")
    print(f"🎯 QUANT AGENT ACCURACY: {accuracy * 100:.2f}%")
    print("==========================================\n")
    
    print("📊 Detailed Classification Report:")
    # 0 = Predicted Down/Flat, 1 = Predicted Up
    print(classification_report(y_test, predictions, target_names=["Sell/Hold (0)", "Buy (1)"]))

    # 7. What did the AI think was most important?
    print("\n🔍 Feature Importance (What the AI cares about most):")
    importances = model.feature_importances_
    feature_importance_df = pd.DataFrame({
        'Indicator': features,
        'Importance Score': importances
    }).sort_values(by='Importance Score', ascending=False)
    
    print(feature_importance_df.to_string(index=False))

if __name__ == "__main__":
    main()