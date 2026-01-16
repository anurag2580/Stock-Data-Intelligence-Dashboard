# 📈 AI-Powered Stock Data Intelligence Dashboard
A full-stack financial analytics platform that provides real-time stock data, interactive visualizations, and **AI-driven price forecasting**. This project goes beyond basic data fetching by implementing **Ensemble Machine Learning** and **High-Performance Caching** to deliver institutional-grade insights.

![Project Banner](https://via.placeholder.com/1000x400?text=Stock+Intelligence+Dashboard+Preview)
### 🏗️ System Architecture
```mermaid
graph TD
    %% User Layer
    User((👤 User))
    Browser[(📱 Web Browser-Dashboard UI)]

    %% Cloud / Deployment Layer
    subgraph "☁️ Render Cloud (Docker Container)"
        style Docker fill:#e1f5fe,stroke:#01579b,stroke-dasharray: 5 5
        Docker[🐳 Docker Container]
        
        subgraph "Backend Core"
            FastAPI[⚡ FastAPI Server]
            Static["📂 Static File Server(HTML/CSS/JS)"]
            Engine[⚙️ Data Engine]
            Cache[🚀 Smart Cache]
        end
        
        subgraph "AI Logic"
            Models[🤖 AI Models<br/>(RandomForest + LinReg)]
            Analyst[📝 Smart Analyst<br/>(RSI/SMA Logic)]
        end
        
        DB[(🗄️ SQLite DB)]
    end

    %% External Layer
    Yahoo[☁️ Yahoo Finance API]

    %% Connections
    User -->|Visits URL| Browser
    Browser -->|1. Load UI| Static
    Browser -->|2. Fetch JSON| FastAPI
    
    FastAPI --> Engine
    Engine --> Cache
    
    Cache -- Miss --> Yahoo
    Yahoo -->|3. Download Data| Engine
    Engine -->|4. Save| DB
    
    Engine --> Models & Analyst
    Models & Analyst -->|5. Insight| FastAPI
    FastAPI -->|6. Response| Browser

    %% Styling
    style FastAPI fill:#bbf,stroke:#333
    style Engine fill:#bbf,stroke:#333
    style Models fill:#cfc,stroke:#333
    style Yahoo fill:#ff9,stroke:#333
```


## 🚀 Key Features

### 📊 Advanced Visualization
- **Real-Time Intraday Charts:** "Day Trading" mode (1D) with minute-by-minute updates.
- **Interactive History:** Zoomable charts for 1M, 1Y, 5Y, and MAX timeframes using **ApexCharts**.
- **Multi-Chart Support:** Toggle seamlessly between Area, Line, and Candlestick views.
- **Smart Formatting:** Automatic currency conversion (e.g., ₹1,500 Cr) and dynamic color-coding (Green/Red) based on market trends.
- 
### ♐ Architecture
- **Smart Caching Layer:** Custom server-side caching prevents redundant API calls, reducing load times to near-zero for frequently accessed assets.
- **Robust Data Engine:** Auto-retry logic and background data persistence using **SQLite** ensure 99.9% uptime even if external APIs glitch.
- **Comparison Tool:** Head-to-head stock performance analysis algorithm.
  
### 🧠 Advanced AI and Machine learning Engine
* **Ensemble Learning:** Uses a weighted combination of **Linear Regression** (for trend analysis) and **Random Forest** (for non-linear pattern recognition) to predict the next day's closing price.
* **Risk Analysis:** Automated volatility scoring system that classifies stocks as "Stable" or "High Risk" based on standard deviation thresholds.

### ⚡ Performance Engineering
* **Data Downsampling:** Optimizes "MAX" charts (20+ years of data) by downsampling daily ticks to weekly intervals, reducing payload size by **80%** without losing trend accuracy.
* **Auto-Retry Logic:** Robust backend that handles external API failures gracefully by retrying connections before returning errors.

---

## 🛠️ Tech Stack
| component | Technologies Used |
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
git clone https://github.com/anurag2580/Stock-Data-Intelligence-Dashboard.git
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

