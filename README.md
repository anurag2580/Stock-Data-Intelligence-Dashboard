# 🚀 Stock Data Intelligence Dashboard

## 🧭 Introduction
This project is a mini financial data platform built to analyze real-time stock market data. It features a robust **FastAPI backend** for data processing and a **responsive frontend dashboard** for visualization.

Key highlights include automated data cleaning, volatility analysis, and a **Machine Learning (Linear Regression)** model that predicts the next day's closing price.

## 🛠️ Tech Stack
* **Language:** Python 3.9+
* **Backend:** FastAPI, Uvicorn
* **Data Processing:** Pandas, NumPy, yfinance
* **Data Visualization:** Matplotlib
* **Machine Learning:** Scikit-learn (Linear Regression)
* **Frontend:** HTML5, CSS3, JavaScript 

## ✨ Key Features
1.  **Real-Time Data Collection:** Fetches live data from NSE via `yfinance`.
2.  **Smart Metrics:** Calculates 7-Day Moving Averages, 52-Week High/Low, and Daily Returns.
3.  **Volatility Analysis:** Computes a custom "Volatility Score" based on standard deviation to assess risk.
4.  **AI Price Prediction:** Uses a Linear Regression model trained on the last 30 days to predict tomorrow's price.
5.  **Interactive Dashboard:** A clean UI to view charts and summaries instantly.

## 📦 Installation & Setup

### 1. Prerequisites
Ensure you have Python installed. Clone this repository or extract the files.
```bash
    pip install - Requirement.txt
```
### 2. Install Dependencies
Open your terminal in the project folder and run or in Vs code terminal: 

### 3. Run The Backend Server
* **FastAPI Server :
       uvicorn main:app --reload
       API will be live at : http://127.0.0.1:8000
* **Swagger Documentation which Help in checking if All api working***
       Swagger Documentation will be live at : http://127.0.0.1:8000/docs
### 4. Launch the Dashboard
   simply double-click index.html to open it in your browser
   will be live at : http://localhost:5500

### 📂 Project Structure
 1.main.py: The entry point for the FastAPI server and REST endpoints.
 2.data_engine.py: Handles data fetching, cleaning, logic, and ML model training.
 3.Frontend/index.html: The frontend visualization dashboard. 
 4.requirements.txt: List of Python dependencies.

### 🧠 Logic & Insights
---Data Cleaning --: Used forward-fill (ffill) to handle missing trading days (e.g., holidays) to ensure continuous time-series data.
---Volatility Score --: Calculated as the rolling standard deviation of the last 7 days. A higher score indicates higher risk/instability.
---ML Model --: The prediction engine uses a simple Linear Regression on the "Close" price of the last 30 days to project the trend for day +1.
 
