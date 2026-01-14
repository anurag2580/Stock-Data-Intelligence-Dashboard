import yfinance as yf
import pandas as pd
import numpy as np
import time
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from database import save_data_to_db

class StockDataEngine:
    def __init__(self):
        self.cache = {} 
        self.CACHE_DURATION = 600 # Cache (10 minutes load)

    def get_processed_data(self, ticker):
        # 1. Check Cache first (Instant load)
        if ticker in self.cache:
            data, timestamp = self.cache[ticker]
            if time.time() - timestamp < self.CACHE_DURATION:
                return data

        # 2. If not in cache, DOWNLOAD IT (Blocking Mode)
        # We try 5 times. We DO NOT return until we have data.
        print(f"📥 Fetching new data for {ticker}...")
        
        max_retries = 5
        for attempt in range(max_retries):
            try:
                # Download MAX data
                df = yf.download(ticker, period="max", interval="1d", progress=False)
                
                # If empty, wait and try again (Yahoo sometimes glitches)
                if df.empty:
                    time.sleep(1)
                    continue

                # Clean MultiIndex
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                
                # Check if we have the right columns
                if 'Close' not in df.columns:
                    time.sleep(1)
                    continue

                df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
                
                # Save to DB (Background backup)
                try: save_data_to_db(ticker, df)
                except: pass

                # Fill missing values
                df.ffill(inplace=True)
                cols = ['Open', 'High', 'Low', 'Close', 'Volume']
                for col in cols: df[col] = df[col].astype(float)

                # Calculate Metrics
                df['Daily_Return'] = (df['Close'] - df['Open']) / df['Open']
                df['52_Week_High'] = df['Close'].rolling(window=252).max()
                df['52_Week_Low'] = df['Close'].rolling(window=252).min()
                df['Volatility_Score'] = df['Close'].rolling(window=7).std()
                
                # SUCCESS! Save to cache and return immediately
                self.cache[ticker] = (df, time.time())
                return df
                
            except Exception as e:
                print(f"⚠️ Attempt {attempt+1} failed: {e}")
                time.sleep(1)

        # Only returns None if 5 attempts (5 seconds) fail completely
        return None
    def get_technical_insight(self, ticker):
        """Generates a professional text summary based on technical indicators."""
        df = self.get_processed_data(ticker)
        if df is None: return "Data unavailable for analysis."
        
        last_close = df['Close'].iloc[-1]
        prev_close = df['Close'].iloc[-2]
        
        # 1. Calculate RSI (Relative Strength Index)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs)).iloc[-1]
        
        # 2. Calculate SMA (Simple Moving Average)
        sma_50 = df['Close'].rolling(window=50).mean().iloc[-1]
        sma_200 = df['Close'].rolling(window=200).mean().iloc[-1]
        
        # 3. Generate "Human-Like" Insight
        insight = f"<b>{ticker} Analysis:</b> The stock closed at <b>₹{round(last_close, 2)}</b>. "
        
        # Trend Logic
        if last_close > sma_50:
            insight += "It is trading <b>above</b> its 50-day moving average, indicating a <b>Bullish (Upward) trend</b>. "
        else:
            insight += "It is trading <b>below</b> its 50-day moving average, indicating a <b>Bearish (Downward) trend</b>. "
            
        # RSI Logic
        if rsi > 70:
            insight += f"However, the RSI is <b>{round(rsi)}</b>, which suggests the stock is <b>Overbought</b> and might see a correction soon."
        elif rsi < 30:
            insight += f"The RSI is <b>{round(rsi)}</b>, suggesting the stock is <b>Oversold</b> and could be undervalued."
        else:
            insight += f"The RSI is stable at <b>{round(rsi)}</b>, showing balanced buying and selling momentum."

        return insight

    def predict_next_day(self, ticker):
        """Ensemble AI: Linear Regression + Random Forest"""
        df = self.get_processed_data(ticker)
        if df is None or len(df) < 60: 
            return {"linear": 0, "random_forest": 0}
        
        recent = df.tail(60).copy()
        X = np.arange(len(recent)).reshape(-1, 1)
        y = recent['Close'].values
        
        # Linear Regression
        model_lr = LinearRegression()
        model_lr.fit(X, y)
        pred_lr = model_lr.predict([[60]])[0]
        
        # Random Forest
        try:
            model_rf = RandomForestRegressor(n_estimators=100, random_state=42)
            model_rf.fit(X, y)
            pred_rf = model_rf.predict([[60]])[0]
        except:
            pred_rf = pred_lr 

        return {
            "linear": round(pred_lr, 2),
            "random_forest": round(pred_rf, 2)
        }