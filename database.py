import sqlite3
import pandas as pd

DB_NAME = "stocks.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_history (
            ticker TEXT,
            date TEXT,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            PRIMARY KEY (ticker, date)
        )
    ''')
    conn.commit()
    conn.close()

def save_data_to_db(ticker, df):
    conn = sqlite3.connect(DB_NAME)
    # Storing data in column
    data = df.copy()
    data.reset_index(inplace=True)
    data['Date'] = data['Date'].astype(str)
    data['ticker'] = ticker
    
    # Save only columns WE need
    cols = ['ticker', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    data = data[cols]
    data.columns = ['ticker', 'date', 'open', 'high', 'low', 'close', 'volume']
    
    try:
        data.to_sql('stock_history', conn, if_exists='append', index=False)
    except:
        pass # Ignore duplicates
    conn.close()

# Initialize on import
init_db()