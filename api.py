from fastapi import FastAPI, HTTPException
import uvicorn
import time

# Import all of your engine scripts!
from cse import main as run_price_miner             
from add_indicators import main as run_indicators
from scout_miner import main as run_micro_miner
from llm_scorer import main as run_llm_scorer
from alt_news_miner import scrape_external_news as run_alt_miner
from alt_news_scorer import main as run_alt_scorer
from macro_miner import fetch_macro_data as run_macro_miner
from merge_data import main as run_merge_data       # 🚀 NEW: Added the CSE Sentiment Merger!
from merge_macro import main as run_merge           
from train_quant import main as run_ai_brain

app = FastAPI(
    title="Crystal Report Quant Engine",
    description="Algorithmic Trading API for the Colombo Stock Exchange",
    version="1.0.0"
)

@app.post("/engine/run-pipeline")
def trigger_full_pipeline():
    start_time = time.time()
    
    try:
        print("\n[API] 1/10: Fetching Daily Stock Prices (CSE)...")
        run_price_miner()
        
        print("\n[API] 2/10: Running Technical Indicators...")
        run_indicators()
        
        print("\n[API] 3/10: Running Micro-Econ Miner (CSE Corporate News)...")
        run_micro_miner()
        
        print("\n[API] 4/10: Scoring CSE Disclosures (Gemini)...")
        run_llm_scorer()
        
        print("\n[API] 5/10: Mining Alternative Web News...")
        run_alt_miner()
        
        print("\n[API] 6/10: Scoring Alternative News (Gemini)...")
        run_alt_scorer()
        
        print("\n[API] 7/10: Pulling Global Macro-Econ Data...")
        run_macro_miner()
        
        print("\n[API] 8/10: Fusing CSE Corporate Sentiment...")
        run_merge_data()  # 🚀 THE MISSING LINK IS NOW ACTIVE!
        
        print("\n[API] 9/10: Fusing Macro & Alt News Streams...")
        run_merge()
        
        print("\n[API] 10/10: Awakening the XGBoost AI...")
        predictions = run_ai_brain() 
        
        execution_time = round(time.time() - start_time, 2)
        
        return {
            "status": "success",
            "message": "Crystal Report Pipeline Executed Successfully.",
            "execution_time_seconds": execution_time,
            "data": predictions
        }

    except Exception as e:
        print(f"\n[API ERROR] Pipeline failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/engine/latest-signals")
def get_latest_signals():
    try:
        predictions = run_ai_brain()
        return {
            "status": "success",
            "data": predictions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not generate signals. Ensure CSVs exist.")

if __name__ == "__main__":
    print("🚀 Starting Crystal Report API Server on Port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)