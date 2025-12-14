# Stock Analysis Dashboard - Frontend

## 🚀 Quick Start

### Prerequisites
- Node.js 14+ installed
- Backend running on port 8000

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

The app will open at `http://localhost:3000`

---

## ✨ Features

### 1. **Searchable Stock Selector**
- 15 pre-loaded Indian stocks (NSE)
- Type-ahead search filtering
- Real-time price display in dropdown
- Last selected stock saved to localStorage
- Custom ticker input option

### 2. **Real-Time Data**
- Auto-refresh every 30 seconds
- Live prices from Yahoo Finance
- Current price with percentage change
- 52-week high/low (backend integration)

### 3. **Multi-Model AI Analysis**
- 4 AI models running in parallel:
  - **Llama 70B**: Sentiment Analysis
  - **Mistral 8x7B**: Technical Analysis
  - **Llama 405B**: Risk Assessment
  - **Llama 70B**: Anomaly Detection

### 4. **Interactive Dashboard**
- BUY/SELL/HOLD recommendations
- Confidence scores with progress bars
- Model agreement metrics
- Price targets and stop loss
- Technical indicators visual

### 5. **Beautiful UI**
- Dark theme (#0f172a background)
- Responsive design (mobile-friendly)
- Smooth animations
- Loading states
- Error handling

---

## 📋 Available Indian Stocks

```
RELIANCE.NS     - Reliance Industries
TCS.NS          - Tata Consultancy Services
INFY.NS         - Infosys
HDFCBANK.NS     - HDFC Bank
ICICIBANK.NS    - ICICI Bank
TATAMOTORS.NS   - Tata Motors
BHARTIARTL.NS   - Bharti Airtel
ITC.NS          - ITC Limited
SBIN.NS         - State Bank of India
WIPRO.NS        - Wipro
LT.NS           - Larsen & Toubro
AXISBANK.NS     - Axis Bank
MARUTI.NS       - Maruti Suzuki
SUNPHARMA.NS    - Sun Pharma
TITAN.NS        - Titan Company
```

---

## 🎨 Component Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   └── Dashboard/
│   │       ├── StockDashboard.js    # Main component
│   │       └── StockDashboard.css   # Styling
│   ├── index.js                      # Entry point
│   └── index.css                     # Global styles
├── .env                              # Environment config
└── package.json                      # Dependencies
```

---

## 🔧 Configuration

### Environment Variables (.env)
```env
REACT_APP_API_URL=http://localhost:8000
```

Change this if your backend runs on a different port.

---

## 📦 Dependencies

- **react**: ^18.2.0
- **react-dom**: ^18.2.0
- **axios**: ^1.6.0 (API calls)
- **recharts**: ^2.10.0 (charting - for future use)

---

## 🎯 API Endpoints Used

### Multi-Model Analysis
```javascript
POST /api/get_stock_analysis_multimodel
Body: {
  "symbol": "RELIANCE",
  "exchange": "NSE"
}
```

### Stock Price (Optional)
```javascript
GET /api/stock/price/:ticker
```

---

## 💡 Usage

1. **Select a Stock**: Click on the dropdown or search for a stock
2. **Custom Ticker**: Click "Add Custom Ticker" to add unlisted stocks
3. **Analyze**: Click "Analyze Stock" button
4. **View Results**: See AI recommendations, model votes, and price targets

---

## 🎨 Customization

### Change Color Theme
Edit `StockDashboard.css`:
```css
/* Primary color */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* BUY color */
color: #10b981;

/* SELL color */
color: #ef4444;

/* HOLD color */
color: #f59e0b;
```

### Add More Stocks
Edit `StockDashboard.js`:
```javascript
const INDIAN_STOCKS = [
  { ticker: 'NEWSTOCK.NS', name: 'New Stock Name' },
  // ... add more
];
```

---

## 🐛 Troubleshooting

### Issue: "CORS Error"
**Solution**: Ensure backend has CORS enabled for `http://localhost:3000`

### Issue: "Cannot connect to backend"
**Solution**: 
1. Check backend is running on port 8000
2. Verify `.env` file has correct API URL

### Issue: "Stock prices not loading"
**Solution**: Backend may not have price endpoint. Prices in dropdown are optional.

---

## 🚀 Deployment

### Build for Production
```bash
npm run build
```

Builds the app for production to the `build/` folder.

### Deploy to Vercel/Netlify
1. Connect your GitHub repo
2. Set environment variable: `REACT_APP_API_URL=https://your-backend-url.com`
3. Deploy!

---

## 📄 License

Private - Internal use only

---

## 🙋 Support

For issues, contact the development team or check the backend logs.
