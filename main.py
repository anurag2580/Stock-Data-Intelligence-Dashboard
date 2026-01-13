from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from data_engine import StockDataEngine
import yfinance as yf
import pandas as pd

app = FastAPI()

# Allow Frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = StockDataEngine()

# Sample Companies List
COMPANIES = {
    "RELIANCE": "RELIANCE.NS", "TCS": "TCS.NS", "INFY": "INFY.NS",
    "HDFCBANK": "HDFCBANK.NS", "TATAMOTORS": "TATAMOTORS.NS", "WIPRO": "WIPRO.NS",
    "SBIN": "SBIN.NS", "ICICIBANK": "ICICIBANK.NS", "ITC": "ITC.NS"
}

@app.get("/companies")
def get_companies():
    return [{"symbol": k} for k in COMPANIES.keys()]

@app.get("/summary/{symbol}")
def get_summary(symbol: str):
    ticker = COMPANIES.get(symbol.upper(), f"{symbol.upper()}.NS")
    df = engine.get_processed_data(ticker)
    if df is None: raise HTTPException(status_code=404, detail="Data not found")
    
    current_price = df['Close'].iloc[-1]
    
    # Helper: Returns both { "percent": 5.2, "value": 120.5 }
    def calculate_metrics(days):
        if len(df) < days: return {"percent": 0.0, "value": 0.0}
        past_price = df['Close'].iloc[-days]
        
        diff = current_price - past_price
        pct = (diff / past_price) * 100
        
        return {
            "percent": round(pct, 2),
            "value": round(diff, 2)
        }

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
    
    # Intraday (1D) metrics
    open_price = df['Open'].iloc[-1]
    returns["1D"] = {
        "percent": round(((current_price - open_price) / open_price) * 100, 2),
        "value": round(current_price - open_price, 2)
    }

    last = df.iloc[-1]
    vol_score = last['Volatility_Score']
    risk_label = "Stable (Low Risk)" if vol_score < 2.0 else "Volatile (High Risk)"
    risk_color = "#00d09c" if vol_score < 2.0 else "#ff4444"

    return {
        "symbol": symbol.upper(),
        "current_price": round(current_price, 2),
        "returns": returns, # Now contains both % and ₹
        "volatility": round(vol_score, 2),
        "risk_label": risk_label,
        "risk_color": risk_color,
        "high_52": round(last['52_Week_High'], 2),
        "low_52": round(last['52_Week_Low'], 2)
    }

    # Volatility Logic
    vol_score = df['Volatility_Score'].iloc[-1]
    risk_label = "Stable (Low Risk)" if vol_score < 2.0 else "Volatile (High Risk)"
    risk_color = "#00d09c" if vol_score < 2.0 else "#ff4444"

    return {
        "symbol": symbol.upper(),
        "current_price": round(current_price, 2),
        "returns": returns, # <--- Sending all returns
        "volatility": round(vol_score, 2),
        "risk_label": risk_label,
        "risk_color": risk_color,
        "high_52": round(df['52_Week_High'].iloc[-1], 2),
        "low_52": round(df['52_Week_Low'].iloc[-1], 2)
    }

@app.get("/predict/{symbol}")
def get_prediction(symbol: str):
    ticker = COMPANIES.get(symbol.upper(), f"{symbol.upper()}.NS")
    return engine.predict_next_day(ticker)

@app.get("/live-data/{symbol}")
async def get_live_data(symbol: str):
    """Returns Intraday (1m) data for 1D chart"""
    ticker = COMPANIES.get(symbol.upper(), f"{symbol.upper()}.NS")
    df = yf.download(ticker, period="1d", interval="1m", progress=False)
    
    if df.empty: raise HTTPException(status_code=404, detail="No live data")
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    
    df.reset_index(inplace=True)
    time_col = 'Datetime' if 'Datetime' in df.columns else 'Date'
    
    return {
        "labels": df[time_col].dt.strftime('%H:%M').tolist(),
        "prices": df['Close'].tolist()
    }

# --- OPTIMIZED CHART ENDPOINT ---
@app.get("/chart-data/{symbol}")
def get_chart_data(symbol: str, time_range: str = "1M"):
    ticker = COMPANIES.get(symbol.upper(), f"{symbol.upper()}.NS")
    df = engine.get_processed_data(ticker)
    
    if df is None: 
        raise HTTPException(status_code=500, detail="Error fetching data")
    
    # 1. Slice Data based on Range
    if time_range == "1W":
        data = df.tail(5)
    elif time_range == "6M":
        data = df.tail(126)
    elif time_range == "1Y":
        data = df.tail(252)
    elif time_range == "5Y":
        # Optimization: For 5Y, take every 2nd day (reduces lag)
        data = df.tail(252 * 5).iloc[::2] 
    elif time_range == "MAX":
        # SUPER OPTIMIZATION: For MAX, take every 5th day (Weekly-ish)
        # This turns 5000 points into 1000, making the chart instant.
        data = df.iloc[::5] 
    else: 
        # Default 1M
        data = df.tail(21)
    
    data = data.copy()
    data.reset_index(inplace=True)

    # 2. Format for ApexCharts
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
    t1 = COMPANIES.get(symbol1.upper(), f"{symbol1.upper()}.NS")
    t2 = COMPANIES.get(symbol2.upper(), f"{symbol2.upper()}.NS")
    
    df1 = engine.get_processed_data(t1)
    df2 = engine.get_processed_data(t2)
    
    if df1 is None or df2 is None: raise HTTPException(status_code=404)
    
    # Compare last 30 days return average
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