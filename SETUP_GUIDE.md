# Multi-Model Stock Analysis - Setup Guide

## Python Version Requirement
**Required:** Python 3.9 or higher

Check your version:
```bash
python --version
```

If you have Python 3.8 or lower, upgrade to Python 3.9+ to use Yahoo Finance integration.

---

## Installation

### 1. Create Virtual Environment (Python 3.9+)
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# Linux/Mac
python3.9 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. Configure Environment
Edit `backend/.env`:
```env
# MarketAux API (for news data)
MARKETAUX_API_KEY=your_key_here

# NVIDIA API (for AI models)
NVIDIA_API_KEY="your_nvidia_api_key_here"
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_MODEL=meta/llama-3.1-405b-instruct
```

---

## Usage

### Run Real-Time Analysis
```bash
# Analyze RELIANCE stock (NSE)
python analyze_stock_realtime.py --symbol RELIANCE

# Analyze TCS stock (BSE)
python analyze_stock_realtime.py --symbol TCS --exchange BSE

# Analyze INFY
python analyze_stock_realtime.py --symbol INFY
```

### Yahoo Finance Ticker Format
- NSE stocks: Auto-converted to `.NS` (e.g., `RELIANCE.NS`)
- BSE stocks: Auto-converted to `.BO` (e.g., `RELIANCE.BO`)

---

## What Changed

### ✅ Added:
- **Yahoo Finance Service** (`backend/app/services/yahoo_finance.py`)
- **Real-time Analysis Script** (`analyze_stock_realtime.py`)
- **yfinance Package** in requirements.txt
- **Python 3.9+ Requirement** noted in requirements.txt

### ❌ Removed:
- Angel One SmartAPI service
- Angel One credentials from .env
- Angel One configuration from config.py
- `smartapi-python` package
- `pandas-ta` package (replaced with `ta`)

### 🔄 Updated:
- **requirements.txt**: Added yfinance, removed Angel One packages
- **Technical Analysis**: Now uses `ta` library instead of `pandas_ta`
- **API Routes**: Updated to use Yahoo Finance service

---

## Features

### Multi-Model Analysis
- **4 AI Models** running in parallel:
  - Sentiment Analysis (Llama 70B)
  - Technical Analysis (Mistral 8x7B)
  - Risk Assessment (Llama 405B)
  - Anomaly Detection (Llama 70B)

### Data Source
- **Yahoo Finance**: Free, real-time data
- **No Authentication Required**
- **Global Market Coverage**

### Output
- Trading recommendation (BUY/SELL/HOLD)
- Confidence score
- Model consensus
- Price targets
- Risk-reward ratio
- Detailed analysis from each model

---

## Next Steps

1. ✅ Upgrade to Python 3.9+ (if needed)
2. ✅ Install dependencies
3. ✅ Run analysis script
4. ✅ Start backend server: `uvicorn app.main:app --reload`
5. ✅ Test API endpoint: `POST /api/get_stock_analysis_multimodel`

**System is ready for production!** 🚀
