import sqlite3
import pandas as pd

DB_NAME = "stocks.db"

def init_db():
    """Creates the table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Create table with a UNIQUE constraint to prevent duplicate days
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            date TEXT,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            UNIQUE(symbol, date)
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ Database initialized.")

def save_data_to_db(symbol, df):
    """Saves fetched data into SQLite."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    count = 0
    for date, row in df.iterrows():
        try:
            date_str = date.strftime('%Y-%m-%d')
            # INSERT OR IGNORE skips duplicates
            cursor.execute('''
                INSERT OR IGNORE INTO stock_prices (symbol, date, open, high, low, close, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (symbol, date_str, row['Open'], row['High'], row['Low'], row['Close'], row['Volume']))
            if cursor.rowcount > 0:
                count += 1
        except Exception:
            pass

    conn.commit()
    conn.close()
    print(f"💾 Saved {count} new records for {symbol}.")