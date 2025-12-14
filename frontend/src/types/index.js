/**
 * TypeScript interfaces for Stock Analysis Platform.
 * These can be used as JSDoc types in JavaScript files.
 */

/**
 * @typedef {Object} StockPrice
 * @property {string} symbol - Stock ticker symbol
 * @property {number} price - Current price
 * @property {number} change - Price change (absolute)
 * @property {number} changePercent - Price change (percentage)
 * @property {number} open - Opening price
 * @property {number} high - Day's high
 * @property {number} low - Day's low
 * @property {number} volume - Trading volume
 * @property {number} avgVolume - Average volume
 * @property {number} marketCap - Market capitalization
 * @property {number} fiftyTwoWeekHigh - 52-week high
 * @property {number} fiftyTwoWeekLow - 52-week low
 * @property {string} timestamp - Last update timestamp
 */

/**
 * @typedef {Object} TechnicalIndicators
 * @property {RSIIndicator} rsi - RSI data
 * @property {MACDIndicator} macd - MACD data
 * @property {SMAIndicator} sma - SMA data
 * @property {BollingerBands} bollingerBands - Bollinger Bands data
 * @property {VolumeIndicator} volume - Volume data
 * @property {string} overallSignal - Overall technical signal
 */

/**
 * @typedef {Object} RSIIndicator
 * @property {number|null} value - RSI value (0-100)
 * @property {'overbought'|'oversold'|'bullish'|'bearish'|'neutral'} signal
 * @property {string} interpretation - Human-readable interpretation
 */

/**
 * @typedef {Object} MACDIndicator
 * @property {number|null} value - MACD line value
 * @property {number|null} signal - Signal line value
 * @property {number|null} histogram - Histogram value
 * @property {'bullish'|'bearish'|'neutral'} interpretation
 */

/**
 * @typedef {Object} SMAIndicator
 * @property {number|null} sma20 - 20-day SMA
 * @property {number|null} sma50 - 50-day SMA
 * @property {'bullish'|'bearish'|'neutral'} signal
 */

/**
 * @typedef {Object} BollingerBands
 * @property {number|null} upper - Upper band
 * @property {number|null} middle - Middle band (SMA)
 * @property {number|null} lower - Lower band
 * @property {'overbought'|'oversold'|'neutral'} signal
 */

/**
 * @typedef {Object} VolumeIndicator
 * @property {number|null} current - Current volume
 * @property {number|null} average - Average volume
 * @property {number} ratio - Volume ratio (current/average)
 * @property {'high'|'low'|'normal'} signal
 */

/**
 * @typedef {Object} AIAnalysis
 * @property {'BUY'|'SELL'|'HOLD'} verdict - AI recommendation
 * @property {number} confidence_score - Confidence (0-100)
 * @property {string} confidence - Confidence level (HIGH/MEDIUM/LOW)
 * @property {number} ensemble_score - Combined model score
 * @property {number} target_price - Target price
 * @property {number} stop_loss - Stop loss price
 * @property {string} reasoning - Analysis reasoning
 * @property {ModelVotes} model_votes - Individual model votes
 * @property {TechnicalIndicators} technical_indicators - Technical data
 * @property {NewsSentiment} news_sentiment - News sentiment
 * @property {AnomalyDetection} anomaly_detection - Anomaly data
 * @property {number} analysis_time_seconds - Analysis duration
 */

/**
 * @typedef {Object} ModelVotes
 * @property {string} sentiment - Sentiment model vote
 * @property {string} technical - Technical model vote
 * @property {string} risk - Risk model vote
 */

/**
 * @typedef {Object} NewsSentiment
 * @property {'positive'|'negative'|'neutral'} overall - Overall sentiment
 * @property {number} average_polarity - Average polarity score
 * @property {number} positive_count - Positive articles count
 * @property {number} negative_count - Negative articles count
 * @property {number} neutral_count - Neutral articles count
 */

/**
 * @typedef {Object} AnomalyDetection
 * @property {boolean} anomaly_detected - Whether anomaly was detected
 * @property {string[]} anomalies - List of detected anomalies
 * @property {string} recommendation - Anomaly recommendation
 */

/**
 * @typedef {Object} Prediction
 * @property {string} id - Prediction ID
 * @property {string} symbol - Stock symbol
 * @property {string} timestamp - Prediction timestamp
 * @property {'BUY'|'SELL'|'HOLD'} verdict - Prediction verdict
 * @property {number} current_price - Price at prediction time
 * @property {number|null} target_price - Target price
 * @property {number|null} actual_price - Actual price (for validation)
 * @property {'PENDING'|'CORRECT'|'INCORRECT'} status - Prediction status
 * @property {number} confidence - Confidence score
 */

/**
 * @typedef {Object} NewsArticle
 * @property {string} title - Article title
 * @property {string} description - Article description
 * @property {string} url - Article URL
 * @property {string} source - News source
 * @property {string} published_at - Publication date
 * @property {'positive'|'negative'|'neutral'} sentiment - Article sentiment
 */

/**
 * @typedef {Object} ChartDataPoint
 * @property {string} date - Date string
 * @property {number} timestamp - Unix timestamp
 * @property {number} open - Open price
 * @property {number} high - High price
 * @property {number} low - Low price
 * @property {number} close - Close price
 * @property {number} volume - Trading volume
 * @property {number} [sma20] - 20-day SMA (optional)
 * @property {number} [sma50] - 50-day SMA (optional)
 * @property {number} [bb_upper] - Bollinger upper band (optional)
 * @property {number} [bb_middle] - Bollinger middle band (optional)
 * @property {number} [bb_lower] - Bollinger lower band (optional)
 */

/**
 * @typedef {Object} WebSocketMessage
 * @property {'price_update'|'subscribed'|'unsubscribed'|'error'} type
 * @property {string} [ticker] - Stock ticker
 * @property {number} [price] - Current price
 * @property {number} [change] - Price change
 * @property {number} [changePercent] - Price change percent
 * @property {string} [timestamp] - Update timestamp
 * @property {string} [error] - Error message
 */

/**
 * @typedef {Object} ToastNotification
 * @property {number} id - Unique toast ID
 * @property {string} message - Toast message
 * @property {'success'|'warning'|'error'|'info'|'price-up'|'price-down'|'prediction'|'market'} type
 */

// Export empty object for module compatibility
export { };
