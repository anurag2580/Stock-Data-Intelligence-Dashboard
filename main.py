from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import matplotlib
matplotlib.use('Agg') # Important: Optimizes Matplotlib for servers
import matplotlib.pyplot as plt
import io

from data_engine import StockDataEngine
from database import init_db

# Initialize DB
init_db()

app = FastAPI()

# Allow frontend to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

COMPANIES = {
    "RELIANCE": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "INFY": "INFY.NS"
}

engine = StockDataEngine(list(COMPANIES.values()))

@app.get("/companies")
def get_companies():
    return [{"symbol": k, "ticker": v} for k, v in COMPANIES.items()]

@app.get("/summary/{symbol}")
def get_summary(symbol: str):
    ticker = COMPANIES.get(symbol.upper())
    df = engine.get_processed_data(ticker)
    if df is None: raise HTTPException(500, "Error")
    
    latest = df.iloc[-1]
    return {
        "symbol": symbol,
        "current_price": round(latest['Close'], 2),
        "high_52": round(latest['52_Week_High'], 2),
        "volatility": round(latest['Volatility_Score'], 2)
    }

@app.get("/predict/{symbol}")
def get_prediction(symbol: str):
    ticker = COMPANIES.get(symbol.upper())
    pred = engine.predict_next_day(ticker)
    # .item() converts numpy arrays/values to a standard Python number safely
    return {"prediction": round(pred.item(), 2)}

# --- MATPLOTLIB CHART ENDPOINT ---
@app.get("/chart/{symbol}")
def get_chart(symbol: str):
    """Generates a PNG image of the stock chart."""
    ticker = COMPANIES.get(symbol.upper())
    df = engine.get_processed_data(ticker)
    
    # Plotting
    data = df.tail(30)
    plt.figure(figsize=(10, 5))
    plt.plot(data.index, data['Close'], color='#2563eb', marker='o')
    plt.title(f"{symbol} - Last 30 Days")
    plt.grid(True, alpha=0.3)
    
    # Save to memory buffer
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close()
    
    return Response(content=buf.getvalue(), media_type="image/png")