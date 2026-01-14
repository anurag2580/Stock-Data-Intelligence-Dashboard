# 1. 📈 Stock Intelligence Dashboard

A full-stack financial analytics platform that combines real-time market data, interactive visualization, and **AI-driven price forecasting**. Built to provide institutional-grade insights with a focus on performance and user experience.

![Project Banner](https://via.placeholder.com/1000x400?text=Stock+Intelligence+Dashboard+Preview)
*(Replace this link with a screenshot of your actual dashboard)*

## 🚀 Key Features

### 📊 Advanced Visualization
- **Real-Time Intraday Charts:** "Day Trading" mode (1D) with minute-by-minute updates.
- **Interactive History:** Zoomable charts for 1M, 1Y, 5Y, and MAX timeframes using **ApexCharts**.
- **Multi-Chart Support:** Toggle seamlessly between Area, Line, and Candlestick views.
- **Smart Formatting:** Automatic currency conversion (e.g., ₹1,500 Cr) and dynamic color-coding (Green/Red) based on market trends.

### 🧠 AI & Machine Learning Engine
- **Ensemble Prediction:** Combines **Linear Regression** (Trend Analysis) and **Random Forest** (Pattern Recognition) to forecast next-day closing prices.
- **Volatility Analysis:** automated risk scoring system that classifies stocks as "Stable" or "High Risk."

### ⚡ Performance & Architecture
- **Smart Caching Layer:** Custom server-side caching prevents redundant API calls, reducing load times to near-zero for frequently accessed assets.
- **Robust Data Engine:** Auto-retry logic and background data persistence using **SQLite** ensure 99.9% uptime even if external APIs glitch.
- **Comparison Tool:** Head-to-head stock performance analysis algorithm.

---

## 🛠️ Tech Stack

| Component | Technologies Used |
| :--- | :--- |
| **Frontend** | HTML5, CSS3 (Glassmorphism), JavaScript (ES6+), ApexCharts.js |
| **Backend** | Python 3.10+, FastAPI (Asynchronous) |
| **Data Science** | Pandas, NumPy, Scikit-Learn |
| **Database** | SQLite3 (Persistent History) |
| **External API** | Yahoo Finance (yfinance) |

---

## ⚙️ Installation & Setup

Follow these steps to run the project locally.

### 1. Clone the Repository
```bash
git clone [https://github.com/your-username/stock-intelligence-dashboard.git](https://github.com/your-username/stock-intelligence-dashboard.git)
cd stock-intelligence-dashboard

### 2. 📂 Create a Virtual Environment (Optional but Recommended)
  python -m venv venv
  # Windows
  venv\Scripts\activate
  # Mac/Linux
  source venv/bin/activate

# 3. Install Dependencies
  pip install -r requirements.txt

# 4. Run the Server
  Start the high-performance FastAPI server:
  uvicorn main:app --reload

# 5. 5. Launch the Dashboard
  Open your browser and navigate to: http://127.0.0.1:8000/static/index.html

  Or Simply open the index.html file directly in your browser

