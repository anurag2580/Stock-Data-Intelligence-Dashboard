from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from data_engine import StockDataEngine
import yfinance as yf
import pandas as pd

app = FastAPI()

# --- ALLOW FRONTEND TO CONNECT (CORS CONFIG) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
engine = StockDataEngine()
# --- COMPANY LIST ---
COMPANIES = {
    "RELIANCE": "RELIANCE.NS", "TCS": "TCS.NS", "INFY": "INFY.NS",
    "HDFCBANK": "HDFCBANK.NS", "TATAMOTORS": "TATAMOTORS.NS", "WIPRO": "WIPRO.NS",
    "SBIN": "SBIN.NS", "ICICIBANK": "ICICIBANK.NS", "ITC": "ITC.NS",
    "ADANIENT": "ADANIENT.NS", "BAJFINANCE": "BAJFINANCE.NS"
}
# --- API ENDPOINTS ---
@app.get("/companies")
def get_companies():
    """Returns list of supported companies."""
    return [{"symbol": k} for k in COMPANIES.keys()]

@app.get("/summary/{symbol}")
def get_summary(symbol: str):
    """
    The Master Endpoint: Returns Price, Returns (% & ₹), Risk, and AI Insight.
    """
    ticker = COMPANIES.get(symbol.upper(), f"{symbol.upper()}.NS")
    df = engine.get_processed_data(ticker)
    
    if df is None: 
        raise HTTPException(status_code=404, detail="Data not found or downloading...")
    
    current_price = df['Close'].iloc[-1]
    last = df.iloc[-1]
    
    # --- A. Calculate Returns (Percent + Value) ---
    def calculate_metrics(days):
        if len(df) < days: return {"percent": 0.0, "value": 0.0}
        past_price = df['Close'].iloc[-days]
        diff = current_price - past_price
        pct = (diff / past_price) * 100
        return {"percent": round(pct, 2), "value": round(diff, 2)}

    # Calculate for all ranges
    returns = {
        "1W": calculate_metrics(5),
        "1M": calculate_metrics(21),
        "6M": calculate_metrics(126),
        "1Y": calculate_metrics(252),
        "5Y": calculate_metrics(252*5),
        "MAX": {
            "percent": round(((current_price - df['Close'].iloc[0]) / df['Close'].iloc[0]) * 100, 2),
            "value": round(current_price - df['Close'].iloc[0], 2)
        }
    }
    
    # (1D) metrics calculation
    open_price = df['Open'].iloc[-1]
    returns["1D"] = {
        "percent": round(((current_price - open_price) / open_price) * 100, 2),
        "value": round(current_price - open_price, 2)
    }

    # --- B. Risk Analysis ---
    vol_score = last['Volatility_Score']
    if vol_score < 2.0:
        risk_label = "Stable (Low Risk)"
        risk_color = "#00d09c" # Green
    else:
        risk_label = "Volatile (High Risk)"
        risk_color = "#ff4444" # Red
    
    # --- C. AI Technical Insight ---
    # (Ensure your data_engine.py has the 'get_technical_insight' method!)
    try:
        smart_insight = engine.get_technical_insight(ticker)
    except AttributeError:
        smart_insight = "AI Analysis initializing..."

    return {
        "symbol": symbol.upper(),
        "current_price": round(current_price, 2),
        "returns": returns,         # Contains {percent, value} for all ranges
        "volatility": round(vol_score, 2),
        "risk_label": risk_label,   # Text: "Stable"
        "risk_color": risk_color,   # Hex: #00d09c
        "high_52": round(last['52_Week_High'], 2),
        "low_52": round(last['52_Week_Low'], 2),
        "insight": smart_insight    # The generated text paragraph
    }

@app.get("/predict/{symbol}")
def get_prediction(symbol: str):
    """Returns AI forecasts (Linear Regression + Random Forest)."""
    ticker = COMPANIES.get(symbol.upper(), f"{symbol.upper()}.NS")
    return engine.predict_next_day(ticker)

@app.get("/live-data/{symbol}")
async def get_live_data(symbol: str):
    """Fetches real-time 1-minute interval data for '1D' view."""
    ticker = COMPANIES.get(symbol.upper(), f"{symbol.upper()}.NS")
    # Fetch only 1 day of live data
    df = yf.download(ticker, period="1d", interval="1m", progress=False)
    
    if df.empty: 
        raise HTTPException(status_code=404, detail="Live market data unavailable")
    
    if isinstance(df.columns, pd.MultiIndex): 
        df.columns = df.columns.get_level_values(0)
    
    df.reset_index(inplace=True)
    time_col = 'Datetime' if 'Datetime' in df.columns else 'Date'
    
    return {
        "labels": df[time_col].dt.strftime('%H:%M').tolist(),
        "prices": df['Close'].tolist()
    }

@app.get("/chart-data/{symbol}")
def get_chart_data(symbol: str, time_range: str = "1M"):
    """Returns formatted chart data with optimizations for MAX view."""
    ticker = COMPANIES.get(symbol.upper(), f"{symbol.upper()}.NS")
    df = engine.get_processed_data(ticker)
    
    if df is None: 
        raise HTTPException(status_code=500, detail="Chart data not ready")
    
    # Slicing & Optimization Logic
    if time_range == "1W":
        data = df.tail(5)
    elif time_range == "6M":
        data = df.tail(126)
    elif time_range == "1Y":
        data = df.tail(252)
    elif time_range == "5Y":
        # Optimization: Every 2nd point for 5Y
        data = df.tail(252 * 5).iloc[::2] 
    elif time_range == "MAX":
        # SUPER OPTIMIZATION: Every 5th point for MAX (Weekly-ish)
        data = df.iloc[::5] 
    else: 
        data = df.tail(21) # Default 1M
    
    data = data.copy()
    data.reset_index(inplace=True)

    chart_data = []
    for _, row in data.iterrows():
        chart_data.append({
            "x": row['Date'].strftime('%Y-%m-%d'),
            "y": [
                round(row['Open'], 2),
                round(row['High'], 2),
                round(row['Low'], 2),
                round(row['Close'], 2)
            ]
        })
    return chart_data

@app.get("/data/{symbol}")
def get_table_data(symbol: str, time_range: str = "1M"):
    """Returns raw history for the table view."""
    ticker = COMPANIES.get(symbol.upper(), f"{symbol.upper()}.NS")
    df = engine.get_processed_data(ticker)
    if df is None: return []

    if time_range == "1W": data = df.tail(5)
    elif time_range == "6M": data = df.tail(126)
    elif time_range == "1Y": data = df.tail(252)
    elif time_range == "5Y": data = df.tail(252*5)
    elif time_range == "MAX": data = df
    else: data = df.tail(21)

    data = data.copy()
    data.reset_index(inplace=True)
    data['Date'] = data['Date'].dt.strftime('%Y-%m-%d')
    return data[['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Daily_Return']].to_dict(orient="records")

@app.get("/compare")
def compare_stocks(symbol1: str, symbol2: str):
    """Compares two stocks based on 30-day performance."""
    t1 = COMPANIES.get(symbol1.upper(), f"{symbol1.upper()}.NS")
    t2 = COMPANIES.get(symbol2.upper(), f"{symbol2.upper()}.NS")
    
    df1 = engine.get_processed_data(t1)
    df2 = engine.get_processed_data(t2)
    
    if df1 is None or df2 is None: 
        raise HTTPException(status_code=404, detail="Stock data not found for comparison")
    
    # Compare average return of last 30 days
    r1 = df1['Daily_Return'].tail(30).mean() * 100
    r2 = df2['Daily_Return'].tail(30).mean() * 100
    
    winner = symbol1 if r1 > r2 else symbol2
    
    return {
        "winner": winner,
        "comparison": {
            symbol1: {"average_return_30d": round(r1, 2)},
            symbol2: {"average_return_30d": round(r2, 2)}
        }
    }