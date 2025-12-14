# Automated Agentic Stock Analysis & Prediction Platform

A self-learning platform that monitors Indian Public Companies (NSE/BSE) in real-time, detects price anomalies, and provides AI-powered trading insights.

## 🏗️ Architecture

### Tech Stack
- **Frontend**: React.js (Mantis Free Admin Template) + Firebase Hosting
- **Backend**: FastAPI (Python) + Render.com
- **Authentication**: Firebase Authentication (Google Sign-In)
- **Database**: Firebase Firestore (NoSQL)
- **AI**: LangChain + GPT-4o + XGBoost
- **Stock Data**: Angel One SmartAPI (WebSocket + Historical API)
- **News Data**: MarketAux API (India-focused)

### System Flow
1. **Watcher Script** → Monitors WebSocket for price anomalies
2. **FastAPI Backend** → Analyzes data with AI agent
3. **Firestore** → Stores predictions and user data
4. **React Frontend** → Displays live insights and charts
5. **Nightly Job** → Validates predictions and retrains model

## 📁 Project Structure

```
agentic/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── main.py            # FastAPI entry point
│   │   ├── config.py          # Configuration & environment variables
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes/
│   │   │       ├── __init__.py
│   │   │       ├── analysis.py    # Stock analysis endpoints
│   │   │       └── auth.py        # Authentication routes
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── angel_one.py       # Angel One SmartAPI integration
│   │   │   ├── marketaux.py       # MarketAux news API
│   │   │   ├── firebase_service.py # Firebase Admin SDK
│   │   │   ├── ai_agent.py        # LangChain + GPT-4o logic
│   │   │   └── technical_analysis.py # RSI, SMA calculations
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py         # Pydantic models
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── helpers.py
│   ├── watcher/
│   │   └── stock_watcher.py       # 24/7 WebSocket monitor
│   ├── ml/
│   │   ├── train_model.py         # XGBoost training
│   │   └── nightly_validator.py   # Prediction validation
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/                   # React Frontend
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard/
│   │   │   │   └── StockDashboard.js
│   │   │   ├── Charts/
│   │   │   │   └── TradingViewChart.js
│   │   │   └── AgentFeed/
│   │   │       └── PredictionFeed.js
│   │   ├── services/
│   │   │   ├── api.js            # API client
│   │   │   └── firebase.js       # Firebase config
│   │   ├── App.js
│   │   └── index.js
│   ├── package.json
│   └── .env.example
│
└── README.md
```

## 🚀 Quick Start

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Add your API keys to .env
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env
# Add your Firebase config
npm start
```

### Watcher Script
```bash
cd backend
python watcher/stock_watcher.py
```

## 🔑 Required API Keys
- Angel One SmartAPI (API Key, Secret)
- MarketAux API Key
- OpenAI API Key (GPT-4o)
- Firebase Service Account JSON

## 📊 Features
- Real-time stock monitoring (NSE/BSE)
- AI-powered sentiment analysis
- Technical indicator analysis (RSI, SMA)
- Self-learning prediction model
- Live agent feed dashboard
- Historical performance tracking
