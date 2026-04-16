import streamlit as st
import requests
import pandas as pd

# --- UI CONFIGURATION ---
st.set_page_config(
    page_title="Crystal Report AI",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a Bloomberg-Terminal aesthetic
st.markdown("""
    <style>
    .big-font {font-size:30px !important; font-weight: bold; color: #00FFcc;}
    .sub-font {font-size:18px !important; color: #aaaaaa;}
    .meter-text {font-size: 24px; font-weight: bold; padding-top: 10px;}
    </style>
""", unsafe_allow_html=True)

# --- S&P 20 COMPANY DICTIONARY ---
# This translates the ticker symbol into the full company name for the detailed view
COMPANY_MAP = {
    "JKH.N0000": "John Keells Holdings PLC",
    "COMB.N0000": "Commercial Bank of Ceylon PLC",
    "LOLC.N0000": "LOLC Holdings PLC",
    "SAMP.N0000": "Sampath Bank PLC",
    "HNB.N0000": "Hatton National Bank PLC",
    "LIOC.N0000": "Lanka IOC PLC",
    "DIAL.N0000": "Dialog Axiata PLC",
    "HAYL.N0000": "Hayleys PLC",
    "MELS.N0000": "Melstacorp PLC",
    "SPEN.N0000": "Aitken Spence PLC",
    "CTC.N0000": "Ceylon Tobacco Company PLC",
    "CARG.N0000": "Cargills (Ceylon) PLC",
    "RICH.N0000": "Richard Pieris and Company PLC",
    "NDB.N0000": "National Development Bank PLC",
    "LION.N0000": "Lion Brewery (Ceylon) PLC",
    "VONE.N0000": "Vallibel One PLC",
    "TKYO.N0000": "Tokyo Cement Company (Lanka) PLC",
    "DFCC.N0000": "DFCC Bank PLC",
    "KHL.N0000": "Keells Hotels PLC",
    "AEL.N0000": "Access Engineering PLC"
}

# --- BROWSER MEMORY (SESSION STATE) ---
if "api_data" not in st.session_state:
    st.session_state.api_data = None
if "selected_stock" not in st.session_state:
    st.session_state.selected_stock = None

# Function to clear selection and go back to main screen
def return_to_main():
    st.session_state.selected_stock = None

# --- API CONNECTION PARAMETERS ---
API_LATEST_SIGNALS = "http://localhost:8000/engine/latest-signals"
API_RUN_PIPELINE = "http://localhost:8000/engine/run-pipeline"

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("⚙️ Master Controls")
    st.write("Trigger the backend microservices.")
    
    if st.button("🚀 Fetch Latest Data", type="primary", use_container_width=True):
        st.warning("Executing 10-Step Pipeline. Please wait...")
        with st.spinner('Scraping, Scoring, and calculating...'):
            try:
                res = requests.post(API_RUN_PIPELINE, timeout=600)
                if res.status_code == 200:
                    st.success("Pipeline Executed Successfully!")
                else:
                    st.error("Pipeline Failed. Check Terminal.")
            except Exception as e:
                st.error(f"API Connection Error: {e}")
                
    st.divider()
    st.write("🟢 API Status: **ONLINE**")

# ==========================================
# VIEW 1: THE DETAILED STOCK DEEP-DIVE
# ==========================================
if st.session_state.selected_stock is not None:
    stock = st.session_state.selected_stock
    symbol = stock['Symbol']
    company_name = COMPANY_MAP.get(symbol, "Unknown Entity")
    conf = float(stock['Confidence_%'])
    signal = stock['Signal']

    # Back Button
    st.button("⬅️ BACK TO TERMINAL", on_click=return_to_main)
    st.divider()

    # Detailed Header
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"<h1>{company_name}</h1>", unsafe_allow_html=True)
        st.markdown(f"<h3>Ticker: <span style='color:#00FFcc;'>{symbol}</span> | Date: {stock['Date']}</h3>", unsafe_allow_html=True)
        
        st.markdown(f"<h2>Master AI Signal:</h2>", unsafe_allow_html=True)
        if "BUY" in signal:
            st.markdown(f"<h1 style='color:#00FF00;'>{signal}</h1>", unsafe_allow_html=True)
        else:
            st.markdown(f"<h1 style='color:#FF4444;'>{signal}</h1>", unsafe_allow_html=True)

    with col2:
        st.info("📊 **AI Intelligence Breakdown**")
        st.write(f"**Closing Price:** LKR {stock['Close']}")
        st.write(f"**Corporate Sentiment:** {stock['LLM_Sentiment']}")
        st.write(f"**Alternative News Sentiment:** {stock['Alt_News_Sentiment']}")

    # The Confidence Meter
    st.divider()
    st.markdown("### 🧠 XGBoost Probability Meter")
    # Streamlit progress bar accepts an integer from 0 to 100
    st.progress(int(conf))
    st.markdown(f"<p class='meter-text'>Calculated Probability of Uptrend: {conf}%</p>", unsafe_allow_html=True)


# ==========================================
# VIEW 2: THE MAIN DASHBOARD
# ==========================================
else:
    st.markdown('<p class="big-font">💎 CSE Price Predictions</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-font">Omniscient AI Quantitative Fund - Colombo Stock Exchange</p>', unsafe_allow_html=True)
    st.divider()
    
    st.subheader("📊 Live Trading Signals")
    st.write("Click a row in the table below to view a detailed breakdown of the AI's calculation.")

    if st.button("📥 Fetch Latest Prices", use_container_width=True):
        with st.spinner("Connecting to Quant Engine..."):
            try:
                response = requests.get(API_LATEST_SIGNALS)
                if response.status_code == 200:
                    data = response.json()
                    # Save the data into Browser Memory
                    st.session_state.api_data = data.get("data", [])
                else:
                    st.error(f"API Error {response.status_code}: Make sure api.py is running!")
            except Exception as e:
                st.error(f"Failed to connect to backend: {e}. Is api.py running on port 8000?")

    # If we have data in memory, display the interactive table
    if st.session_state.api_data:
        df = pd.DataFrame(st.session_state.api_data)
        df = df.sort_values(by=['Confidence_%'], ascending=False)
        display_cols = ['Symbol', 'Date', 'Close', 'LLM_Sentiment', 'Alt_News_Sentiment', 'Confidence_%', 'Signal']
        df_display = df[display_cols]
        
        def highlight_signals(val):
            if 'BUY' in str(val):
                return 'color: #00FF00; font-weight: bold;'
            elif 'HOLD' in str(val):
                return 'color: #FF4444; font-weight: bold;'
            return ''
        
        styled_df = df_display.style.applymap(highlight_signals, subset=['Signal'])
        
        # 🚀 THE INTERACTIVITY UPGRADE: Single-click selection
        event = st.dataframe(
            styled_df, 
            use_container_width=True, 
            height=600,
            on_select="rerun",           # Triggers a UI refresh when a row is clicked
            selection_mode="single-row"  # Only allows one stock to be clicked at a time
        )
        
        # If the user clicks a row, save that row's data and reload the page into View 1
        if len(event.selection.rows) > 0:
            selected_index = event.selection.rows[0]
            st.session_state.selected_stock = df_display.iloc[selected_index].to_dict()
            st.rerun()