import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from database import save_data_to_db  # Import our DB function

class StockDataEngine:
    def __init__(self, tickers):
        self.tickers = tickers

    def get_processed_data(self, ticker):
        try:
            # 1. Fetch Data
            df = yf.download(ticker, period="2y", interval="1d", progress=False)
            
            # CHECK: If data is empty, stop here
            if df is None or df.empty:
                print(f"⚠️ No data found for {ticker}")
                return None

            # 2. Save to SQLite
            # Wrap in try/except so DB errors don't crash the whole app
            try:
                save_data_to_db(ticker, df)
            except Exception as db_err:
                print(f"⚠️ DB Save Error: {db_err}")

            # 3. Clean & Metrics
            df.ffill(inplace=True) 
            
            # ERROR PREVENTION: Ensure we have enough data for calculations
            if len(df) < 30:
                return None

            df['Daily_Return'] = (df['Close'] - df['Open']) / df['Open']
            df['52_Week_High'] = df['Close'].rolling(window=252).max()
            df['52_Week_Low'] = df['Close'].rolling(window=252).min()
            df['Volatility_Score'] = df['Close'].rolling(window=7).std()
            
            return df
            
        except Exception as e:
            print(f"❌ Critical Error in Data Engine: {e}")
            return None

    def predict_next_day(self, ticker):
        """AI Feature: Predicts next day price using Linear Regression."""
        df = self.get_processed_data(ticker)
        if df is None: return None
        
        # Use last 30 days for training
        recent = df.tail(30).copy()
        recent['Day_ID'] = np.arange(len(recent))
        
        X = recent[['Day_ID']]
        y = recent['Close']
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Predict day 30 (the next day)
        prediction = model.predict([[30]])
        return prediction[0]