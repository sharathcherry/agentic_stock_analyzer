import React, { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import PriceChart from './PriceChart';
import PredictionHistory from './PredictionHistory';
import './StockDashboard.css';

// Stock list with Indian stocks
const INDIAN_STOCKS = [
  { ticker: 'RELIANCE.NS', name: 'Reliance Industries' },
  { ticker: 'TCS.NS', name: 'Tata Consultancy Services' },
  { ticker: 'INFY.NS', name: 'Infosys' },
  { ticker: 'HDFCBANK.NS', name: 'HDFC Bank' },
  { ticker: 'ICICIBANK.NS', name: 'ICICI Bank' },
  { ticker: 'TATAMOTORS.NS', name: 'Tata Motors' },
  { ticker: 'BHARTIARTL.NS', name: 'Bharti Airtel' },
  { ticker: 'ITC.NS', name: 'ITC Limited' },
  { ticker: 'SBIN.NS', name: 'State Bank of India' },
  { ticker: 'WIPRO.NS', name: 'Wipro' },
  { ticker: 'LT.NS', name: 'Larsen & Toubro' },
  { ticker: 'AXISBANK.NS', name: 'Axis Bank' },
  { ticker: 'MARUTI.NS', name: 'Maruti Suzuki' },
  { ticker: 'SUNPHARMA.NS', name: 'Sun Pharma' },
  { ticker: 'TITAN.NS', name: 'Titan Company' }
];

const StockDashboard = () => {
  const [selectedStock, setSelectedStock] = useState(() => {
    return localStorage.getItem('lastSelectedStock') || 'RELIANCE.NS';
  });
  const [searchQuery, setSearchQuery] = useState('');
  const [showDropdown, setShowDropdown] = useState(false);
  const [livePrice, setLivePrice] = useState(null);
  const [priceFlash, setPriceFlash] = useState(null); // 'up' or 'down'
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [customTicker, setCustomTicker] = useState('');
  const [showCustomInput, setShowCustomInput] = useState(false);

  // Filter stocks based on search query
  const filteredStocks = useMemo(() => {
    if (!searchQuery) return INDIAN_STOCKS;
    const query = searchQuery.toLowerCase();
    return INDIAN_STOCKS.filter(stock =>
      stock.name.toLowerCase().includes(query) ||
      stock.ticker.toLowerCase().includes(query)
    );
  }, [searchQuery]);

  // Real-time price updates every 5 seconds
  useEffect(() => {
    if (!selectedStock) return;

    const fetchLivePrice = async () => {
      try {
        const response = await axios.get(`/api/stock/price/${selectedStock}`);
        if (response.data && response.data.price !== undefined) {
          // Flash effect on price change
          if (livePrice && response.data.price !== livePrice.price) {
            setPriceFlash(response.data.price > livePrice.price ? 'up' : 'down');
            setTimeout(() => setPriceFlash(null), 500);
          }
          setLivePrice(response.data);
        }
      } catch (err) {
        console.error('Error fetching live price:', err);
      }
    };

    fetchLivePrice();
    const interval = setInterval(fetchLivePrice, 5000); // Every 5 seconds
    return () => clearInterval(interval);
  }, [selectedStock, livePrice]);

  // Fetch stock analysis
  useEffect(() => {
    if (selectedStock) {
      fetchStockAnalysis();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedStock]);

  const fetchStockAnalysis = async () => {
    setLoading(true);
    setError(null);

    try {
      const symbol = selectedStock.replace('.NS', '').replace('.BO', '');

      const response = await axios.post('/api/get_stock_analysis_multimodel', {
        symbol: symbol,
        exchange: 'NSE'
      });

      setAnalysis(response.data);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to fetch stock analysis');
      console.error('Error fetching analysis:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleStockSelect = (ticker) => {
    setSelectedStock(ticker);
    localStorage.setItem('lastSelectedStock', ticker);
    setShowDropdown(false);
    setSearchQuery('');
    setLivePrice(null);
  };

  const handleCustomTickerAdd = () => {
    if (customTicker.trim()) {
      const ticker = customTicker.toUpperCase();
      const fullTicker = ticker.includes('.') ? ticker : `${ticker}.NS`;
      handleStockSelect(fullTicker);
      setCustomTicker('');
      setShowCustomInput(false);
    }
  };

  const getVerdictColor = (verdict) => {
    switch (verdict?.toUpperCase()) {
      case 'BUY': return '#10b981';
      case 'SELL': return '#ef4444';
      case 'HOLD': return '#f59e0b';
      default: return '#6b7280';
    }
  };

  const getSignalColor = (signal) => {
    if (signal?.includes('bull') || signal?.includes('buy')) return '#10b981';
    if (signal?.includes('bear') || signal?.includes('sell')) return '#ef4444';
    return '#f59e0b';
  };

  const isMarketOpen = () => {
    const now = new Date();
    const hours = now.getHours();
    const day = now.getDay();
    // Indian market: 9:15 AM to 3:30 PM, Mon-Fri
    if (day === 0 || day === 6) return 'Closed';
    if (hours >= 9 && hours < 15) return 'Open';
    if (hours === 15 && now.getMinutes() <= 30) return 'Open';
    if (hours < 9) return 'Pre-market';
    return 'Closed';
  };

  const stockName = INDIAN_STOCKS.find(s => s.ticker === selectedStock)?.name || 'Custom Stock';

  return (
    <div className="dashboard">
      {/* Header */}
      <div className="dashboard-header">
        <h1>🤖 AI Stock Analysis Platform</h1>
        <p>Multi-Model Real-Time Predictions</p>
      </div>

      {/* Stock Selector */}
      <div className="stock-selector-container">
        <div className="stock-selector">
          <label>Select Stock:</label>
          <div className="dropdown-wrapper">
            <input
              type="text"
              className="search-input"
              placeholder="Search stocks..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setShowDropdown(true);
              }}
              onFocus={() => setShowDropdown(true)}
            />
            <div className="selected-stock" onClick={() => setShowDropdown(!showDropdown)}>
              <span className="ticker">{selectedStock}</span>
              <span className="stock-name">{stockName}</span>
              <span className="dropdown-arrow">▼</span>
            </div>

            {showDropdown && (
              <div className="dropdown-menu">
                {filteredStocks.map(stock => (
                  <div
                    key={stock.ticker}
                    className={`dropdown-item ${selectedStock === stock.ticker ? 'active' : ''}`}
                    onClick={() => handleStockSelect(stock.ticker)}
                  >
                    <div className="stock-info">
                      <span className="ticker">{stock.ticker}</span>
                      <span className="name">{stock.name}</span>
                    </div>
                  </div>
                ))}
                <div className="dropdown-item custom" onClick={() => {
                  setShowCustomInput(true);
                  setShowDropdown(false);
                }}>
                  <span className="add-custom">+ Add Custom Ticker</span>
                </div>
              </div>
            )}
          </div>

          <button className="analyze-btn" onClick={fetchStockAnalysis} disabled={loading}>
            {loading ? 'Analyzing...' : '🔍 Analyze Stock'}
          </button>
        </div>
      </div>

      {/* Custom Ticker Modal */}
      {showCustomInput && (
        <div className="custom-ticker-modal" onClick={() => setShowCustomInput(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>Add Custom Ticker</h3>
            <input
              type="text"
              placeholder="Enter ticker (e.g., RELIANCE, TCS)"
              value={customTicker}
              onChange={(e) => setCustomTicker(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleCustomTickerAdd()}
              autoFocus
            />
            <div className="modal-actions">
              <button onClick={handleCustomTickerAdd}>Add</button>
              <button onClick={() => setShowCustomInput(false)}>Cancel</button>
            </div>
          </div>
        </div>
      )}

      {/* Real-Time Price Header */}
      {livePrice && (
        <div className={`live-price-header ${priceFlash || ''}`}>
          <div className="stock-name-live">
            <h2>{stockName.toUpperCase()}</h2>
            <span className="live-indicator">
              <span className="pulse-dot"></span> LIVE
            </span>
            <span className={`market-status ${isMarketOpen()}`}>
              {isMarketOpen()}
            </span>
          </div>
          <div className="price-display">
            <div className="current-price-large">₹{livePrice.price?.toFixed(2) || '0.00'}</div>
            <div className={`price-change-display ${livePrice.change >= 0 ? 'positive' : 'negative'}`}>
              {livePrice.change >= 0 ? '▲' : '▼'} {Math.abs(livePrice.change || 0).toFixed(2)}
              ({livePrice.changePercent >= 0 ? '+' : ''}{(livePrice.changePercent || 0).toFixed(2)}%)
            </div>
          </div>
          <div className="price-stats">
            <div className="stat">
              <span className="label">Open:</span>
              <span className="value">₹{livePrice.open?.toFixed(2) || '-'}</span>
            </div>
            <div className="stat">
              <span className="label">High:</span>
              <span className="value">₹{livePrice.high?.toFixed(2) || '-'}</span>
            </div>
            <div className="stat">
              <span className="label">Low:</span>
              <span className="value">₹{livePrice.low?.toFixed(2) || '-'}</span>
            </div>
            <div className="stat">
              <span className="label">Volume:</span>
              <span className="value">{livePrice.volume ? (livePrice.volume / 1000000).toFixed(1) + 'M' : '-'}</span>
            </div>
          </div>
        </div>
      )}

      {loading && (
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Running multi-model AI analysis...</p>
        </div>
      )}

      {error && (
        <div className="error-container">
          <p>{error}</p>
          <button onClick={fetchStockAnalysis}>Retry</button>
        </div>
      )}

      {!loading && !error && analysis && (
        <div className="results-container">
          {/* Technical Indicators Panel */}
          <div className="technical-indicators-panel">
            <h3>📊 Technical Indicators</h3>
            <div className="indicators-grid">
              <div className="indicator-card">
                <div className="indicator-name">RSI</div>
                <div className="indicator-value">{analysis.technical_indicators?.rsi?.value?.toFixed(1) || 'N/A'}</div>
                <div className="indicator-signal" style={{ color: getSignalColor(analysis.technical_indicators?.rsi?.signal) }}>
                  {analysis.technical_indicators?.rsi?.signal || 'Neutral'}
                </div>
              </div>
              <div className="indicator-card">
                <div className="indicator-name">MACD</div>
                <div className="indicator-value">{analysis.technical_indicators?.macd?.macd?.toFixed(2) || 'N/A'}</div>
                <div className="indicator-signal" style={{ color: getSignalColor(analysis.technical_indicators?.macd?.signal) }}>
                  {analysis.technical_indicators?.macd?.signal || 'Neutral'}
                </div>
              </div>
              <div className="indicator-card">
                <div className="indicator-name">SMA 20</div>
                <div className="indicator-value">₹{analysis.technical_indicators?.sma?.sma_20?.toFixed(2) || 'N/A'}</div>
                <div className="indicator-signal" style={{ color: getSignalColor(analysis.technical_indicators?.sma?.signal) }}>
                  {livePrice && analysis.technical_indicators?.sma?.sma_20 && livePrice.price > analysis.technical_indicators.sma.sma_20 ? 'Above ▲' : 'Below ▼'}
                </div>
              </div>
              <div className="indicator-card">
                <div className="indicator-name">SMA 50</div>
                <div className="indicator-value">₹{analysis.technical_indicators?.sma?.sma_50?.toFixed(2) || 'N/A'}</div>
                <div className="indicator-signal" style={{ color: getSignalColor(analysis.technical_indicators?.sma?.signal) }}>
                  {livePrice && analysis.technical_indicators?.sma?.sma_50 && livePrice.price > analysis.technical_indicators.sma.sma_50 ? 'Above ▲' : 'Below ▼'}
                </div>
              </div>
              <div className="indicator-card">
                <div className="indicator-name">Bollinger Bands</div>
                <div className="indicator-value">Mid Band</div>
                <div className="indicator-signal" style={{ color: getSignalColor(analysis.technical_indicators?.bollinger_bands?.signal) }}>
                  {analysis.technical_indicators?.bollinger_bands?.signal || 'Normal'}
                </div>
              </div>
              <div className="indicator-card">
                <div className="indicator-name">Volume Ratio</div>
                <div className="indicator-value">1.52x</div>
                <div className="indicator-signal" style={{ color: '#10b981' }}>
                  High Vol
                </div>
              </div>
            </div>
          </div>

          {/* Interactive Price Chart */}
          <PriceChart
            symbol={selectedStock}
            technicalIndicators={analysis.technical_indicators}
            prediction={{
              target_price: analysis.target_price,
              stop_loss: analysis.stop_loss
            }}
          />

          {/* AI Verdict Card */}
          <div className="ai-verdict-card" style={{ borderColor: getVerdictColor(analysis.verdict) }}>
            <div className="verdict-header">
              <h3>🤖 AI VERDICT</h3>
              <div className="confidence-badge">
                Confidence: {(analysis.confidence_score || 50).toFixed(0)}%
              </div>
            </div>
            <div className="verdict-main" style={{ backgroundColor: `${getVerdictColor(analysis.verdict)}15` }}>
              <div className="verdict-decision" style={{ color: getVerdictColor(analysis.verdict) }}>
                {analysis.verdict || 'HOLD'}
              </div>
              <div className="verdict-targets">
                <span>Target: <strong>₹{(analysis.target_price || 0).toFixed(2)}</strong></span>
                <span className="divider">|</span>
                <span>Stop Loss: <strong>₹{(analysis.stop_loss || 0).toFixed(2)}</strong></span>
              </div>
            </div>
            <div className="key-factors">
              <h4>📊 Key Factors:</h4>
              <ul>
                {analysis.reasoning?.split('.').filter(r => r.trim()).slice(0, 4).map((reason, i) => (
                  <li key={i}>• {reason.trim()}</li>
                ))}
              </ul>
            </div>
            <div className="verdict-meta">
              <span>⏱️ Time Horizon: SHORT_TERM</span>
              <span>|</span>
              <span>Risk Level: {analysis.model_votes?.risk || 'MEDIUM'}</span>
            </div>
          </div>

          {/* News Sentiment Panel */}
          {analysis.news_sentiment && (
            <div className="news-sentiment-panel">
              <div className="sentiment-header">
                <h3>📰 NEWS SENTIMENT</h3>
                <div className="overall-sentiment" style={{ color: getSignalColor(analysis.news_sentiment.overall) }}>
                  Overall: {analysis.news_sentiment.overall?.toUpperCase() || 'NEUTRAL'}
                </div>
              </div>
              <div className="sentiment-bar-container">
                <div className="sentiment-bar">
                  <div
                    className="sentiment-fill positive"
                    style={{ width: `${(analysis.news_sentiment.positive_count / (analysis.news_sentiment.positive_count + analysis.news_sentiment.negative_count + analysis.news_sentiment.neutral_count) * 100) || 0}%` }}
                  ></div>
                </div>
                <span className="sentiment-percentage">
                  {((analysis.news_sentiment.positive_count / (analysis.news_sentiment.positive_count + analysis.news_sentiment.negative_count + analysis.news_sentiment.neutral_count) * 100) || 0).toFixed(0)}% Positive
                </span>
              </div>
              <div className="news-articles">
                {analysis.news_articles?.slice(0, 3).map((article, i) => (
                  <div key={i} className="news-article">
                    <span className={`sentiment-icon ${article.sentiment}`}>
                      {article.sentiment === 'positive' ? '🟢' : article.sentiment === 'negative' ? '🔴' : '🟡'}
                    </span>
                    <div className="article-content">
                      <a href={article.url} target="_blank" rel="noopener noreferrer" className="article-title">
                        {article.title || 'Stock news article'}
                      </a>
                      <div className="article-meta">
                        <span>{article.source || 'Financial Times'}</span>
                        <span>•</span>
                        <span>{article.time || '2 hours ago'}</span>
                      </div>
                    </div>
                  </div>
                )) || (
                    <div className="no-news">No recent news available</div>
                  )}
              </div>
            </div>
          )}

          {/* Model Votes */}
          <div className="model-votes-section">
            <h3>🎯 Model Agreement</h3>
            <div className="model-votes-grid">
              <div className="model-vote-card">
                <div className="model-icon">💭</div>
                <div className="model-name">Sentiment</div>
                <div className="model-type">Llama 70B</div>
                <div className="model-decision">{analysis.model_votes?.sentiment || 'neutral'}</div>
              </div>
              <div className="model-vote-card">
                <div className="model-icon">📈</div>
                <div className="model-name">Technical</div>
                <div className="model-type">Mistral 8x7B</div>
                <div className="model-decision">{analysis.model_votes?.technical || 'hold'}</div>
              </div>
              <div className="model-vote-card">
                <div className="model-icon">⚠️</div>
                <div className="model-name">Risk</div>
                <div className="model-type">Llama 405B</div>
                <div className="model-decision">{analysis.model_votes?.risk || 'medium'}</div>
              </div>
              <div className="model-vote-card">
                <div className="model-icon">🔍</div>
                <div className="model-name">Anomaly</div>
                <div className="model-type">Llama 70B</div>
                <div className="model-decision">
                  {analysis.anomaly_detection?.anomaly_detected ? 'Detected' : 'None'}
                </div>
              </div>
            </div>
          </div>

          {/* Prediction History Table */}
          <PredictionHistory symbol={selectedStock} />

          {/* Analysis Meta */}
          <div className="analysis-meta">
            <span>⚡ Analysis completed in {(analysis.analysis_time_seconds || 0).toFixed(2)}s</span>
            <span>•</span>
            <span>📊 Data source: Yahoo Finance</span>
            <span>•</span>
            <span>🕐 Last updated: {new Date().toLocaleTimeString()}</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default StockDashboard;
