# 📈 AI-Powered Stock Intelligence Dashboard

A full-stack financial analytics platform that provides real-time stock data, interactive visualizations, and **AI-driven price forecasting**. This project goes beyond basic data fetching by implementing **Ensemble Machine Learning** and **High-Performance Caching** to deliver institutional-grade insights.

![Project Banner](https://via.placeholder.com/1000x400?text=Stock+Intelligence+Dashboard+Preview)
*(Replace this link with a screenshot of your actual dashboard)*

## 🚀 Key Features

### 📊 Professional Visualization
* **Live "Day Trading" Mode (1D):** Switches to minute-by-minute intraday data ticks for real-time market monitoring.
* **Interactive History:** Zoomable ApexCharts for 1M, 1Y, 5Y, and MAX timeframes.
* **Smart Formatting:** Automatically formats large figures (e.g., "₹1,500 Cr") and uses dynamic color-coding (Green/Red) for profit/loss visibility.

### 🧠 Advanced AI Engine
* **Ensemble Learning:** Uses a weighted combination of **Linear Regression** (for trend analysis) and **Random Forest** (for non-linear pattern recognition) to predict the next day's closing price.
* **Risk Analysis:** Automated volatility scoring system that classifies stocks as "Stable" or "High Risk" based on standard deviation thresholds.

### ⚡ Performance Engineering
* **Smart Caching System:** Implements server-side caching to serve frequently requested data instantly (0ms latency), resolving the common "double-click" loading issue.
* **Data Downsampling:** Optimizes "MAX" charts (20+ years of data) by downsampling daily ticks to weekly intervals, reducing payload size by **80%** without losing trend accuracy.
* **Auto-Retry Logic:** Robust backend that handles external API failures gracefully by retrying connections before returning errors.

---

## 🛠️ Tech Stack

| Layer | Technologies Used |
| :--- | :--- |
| **Frontend** | HTML5, CSS3 (Glassmorphism), JavaScript (ES6+), ApexCharts.js |
| **Backend** | Python 3.10+, FastAPI (Asynchronous High-Performance API) |
| **ML & Data** | Pandas, NumPy, Scikit-Learn (RandomForest, LinearRegression) |
| **Persistence** | SQLite3 (Local History Backup) |
| **Data Source** | Yahoo Finance (yfinance) |

---

## ⚙️ Installation & Setup

Follow these steps to run the project locally.

### 1. Clone the Repository
```bash
git clone [https://github.com/your-username/stock-dashboard.git](https://github.com/your-username/stock-dashboard.git)
cd stock-dashboard
```
### 2.Create a Virtual Environment (Optional but Recommended)(Python must be installed)
```
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```
### 3. Install Dependencies
```bash
   pip install -r requirements.txt
```
### 4.Run the Server
 Start the FastAPI backend
```bash
uvicorn main:app --reload
```
### 5.Launch the Dashboard
Open your browser and navigate to: http://127.0.0.1:8000/static/index.html(Or simply open the index.html file directly in your browser)

# 📂 Project Structure
stock-dashboard/
├── main.py              # API Gateway & Route Logic
├── data_engine.py       # Core Logic: Caching, AI Models, Data Fetching
├── database.py          # SQLite persistence layer
├── index.html           # Frontend Dashboard (Single Page App)
├── requirements.txt     # Python Dependencies
└── stocks.db            # Local Database (Auto-generated)
# 📸 Screenshots
1.Interactive Dashboard(Live 1d View)
2.AI Predictions & Risk Analysis
3. Comparison Tool

# 📬 Contact
Anurag Ray Data Analyst & Full Stack Developer |anurag-rai-403037245 |anuragrai2580@gamil.com |

