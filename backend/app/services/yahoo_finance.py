"""
Yahoo Finance Data Service
Fetches real-time and historical stock data using yfinance library.
"""
import yfinance as yf
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class YahooFinanceService:
    """Service for fetching stock data from Yahoo Finance."""
    
    @staticmethod
    def get_stock_data(
        ticker: str,
        period: str = "1mo",
        interval: str = "1d"
    ) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive stock data including price and historical data.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'RELIANCE.NS' for NSE, 'RELIANCE.BO' for BSE)
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            
        Returns:
            Dictionary containing current price, previous close, and historical data
        """
        try:
            logger.info(f"Fetching data for {ticker}")
            stock = yf.Ticker(ticker)
            
            # Get current info
            info = stock.info
            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            previous_close = info.get('previousClose')
            
            if not current_price or not previous_close:
                logger.error(f"Could not fetch price data for {ticker}")
                return None
            
            # Get historical data
            hist = stock.history(period=period, interval=interval)
            
            if hist.empty:
                logger.error(f"No historical data available for {ticker}")
                return None
            
            # Convert to format expected by orchestrator
            historical_data = []
            for index, row in hist.iterrows():
                historical_data.append({
                    'timestamp': index.isoformat(),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume'])
                })
            
            # Calculate price change
            price_change_percent = ((current_price - previous_close) / previous_close) * 100
            
            return {
                'ticker': ticker,
                'current_price': round(current_price, 2),
                'previous_close': round(previous_close, 2),
                'price_change_percent': round(price_change_percent, 2),
                'historical_data': {'data': historical_data},
                'info': {
                    'name': info.get('longName', ticker),
                    'symbol': info.get('symbol', ticker),
                    'exchange': info.get('exchange', 'Unknown'),
                    'currency': info.get('currency', 'INR'),
                    'market_cap': info.get('marketCap'),
                    'volume': info.get('volume'),
                    'avg_volume': info.get('averageVolume'),
                    '52_week_high': info.get('fiftyTwoWeekHigh'),
                    '52_week_low': info.get('fiftyTwoWeekLow'),
                }
            }
            
        except Exception as e:
            logger.error(f"Error fetching Yahoo Finance data for {ticker}: {str(e)}")
            return None
    
    @staticmethod
    def get_ltp(ticker: str) -> Optional[float]:
        """
        Get Last Traded Price for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Last traded price or None
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            return info.get('currentPrice') or info.get('regularMarketPrice')
        except Exception as e:
            logger.error(f"Error fetching LTP for {ticker}: {str(e)}")
            return None
    
    @staticmethod
    def get_historical_data(
        ticker: str,
        period: str = "1mo",
        interval: str = "1d"
    ) -> Optional[Dict[str, List]]:
        """
        Get historical candlestick data.
        
        Args:
            ticker: Stock ticker symbol
            period: Data period
            interval: Candle interval
            
        Returns:
            Dictionary with 'data' key containing list of OHLC candles
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period, interval=interval)
            
            if hist.empty:
                return None
            
            historical_data = []
            for index, row in hist.iterrows():
                historical_data.append({
                    'timestamp': index.isoformat(),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume'])
                })
            
            return {'data': historical_data}
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {ticker}: {str(e)}")
            return None
    
    @staticmethod
    def convert_symbol_to_yahoo(symbol: str, exchange: str = "AUTO") -> str:
        """
        Convert stock symbol to Yahoo Finance format.
        Intelligently detects US vs Indian stocks.
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE', 'AAPL', 'MSFT')
            exchange: Exchange ('NSE', 'BSE', or 'AUTO' for auto-detection)
            
        Returns:
            Yahoo Finance ticker (e.g., 'RELIANCE.NS', 'AAPL', 'MSFT')
        """
        # Remove -EQ suffix if present (Indian stocks)
        symbol = symbol.replace('-EQ', '').strip().upper()
        
        # Common US tech stocks (FAANG + major tech)
        us_tech_stocks = {
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'META', 'TSLA', 'NVDA',
            'AMD', 'INTC', 'NFLX', 'ORCL', 'CRM', 'ADBE', 'CSCO', 'IBM',
            'PYPL', 'UBER', 'LYFT', 'SNAP', 'TWTR', 'SQ', 'SHOP', 'SPOT',
            'ZOOM', 'DOCU', 'OKTA', 'NET', 'CRWD', 'ZS', 'DDOG', 'MDB'
        }
        
        # Major US companies across sectors
        us_stocks = {
            'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C',  # Banks
            'JNJ', 'PFE', 'UNH', 'ABT', 'TMO', 'MRK',  # Healthcare
            'XOM', 'CVX', 'COP', 'SLB',  # Energy
            'WMT', 'HD', 'NKE', 'MCD', 'SBUX', 'KO', 'PEP',  # Retail/Consumer
            'BA', 'CAT', 'GE', 'MMM', 'HON',  # Industrial
            'V', 'MA', 'DIS', 'CMCSA',  # Others
        }
        
        # Combine all known US stocks
        known_us_stocks = us_tech_stocks | us_stocks
        
        # Common Indian stocks (NSE)
        known_indian_stocks = {
            # IT Services
            'TCS', 'INFY', 'WIPRO', 'HCLTECH', 'TECHM', 'LTI', 'LTIM', 'COFORGE',
            'PERSISTENT', 'MPHASIS', 'MINDTREE',
            
            # Banking & Finance  
            'HDFCBANK', 'ICICIBANK', 'SBIN', 'AXISBANK', 'KOTAKBANK', 'INDUSINDBK',
            'BANDHANBNK', 'FEDERALBNK', 'IDFCFIRSTB', 'PNB', 'BANKBARODA',
            'BAJFINANCE', 'BAJAJFINSV', 'HDFC', 'CHOLAFIN', 'MUTHOOTFIN', 'LICHSGFIN',
            
            # Energy & Oil
            'RELIANCE', 'ONGC', 'IOC', 'BPCL', 'HINDPETRO', 'GAIL', 'NTPC',
            'POWERGRID', 'ADANIGREEN', 'ADANIPOWER', 'TATAPOWER', 'TORNTPOWER',
            
            # Automobiles
            'TATAMOTORS', 'MARUTI', 'M&M', 'BAJAJ-AUTO', 'HEROMOTOCO', 'EICHERMOT',
            'ASHOKLEY', 'ESCORTS', 'TVS', 'TVSMOTOR', 'APOLLOTYRE', 'MRF',
            
            # FMCG & Consumer
            'HINDUNILVR', 'ITC', 'NESTLEIND', 'BRITANNIA', 'DABUR', 'MARICO',
            'GODREJCP', 'COLPAL', 'EMAMILTD', 'VBL', 'TATACONSUM', 'PGHH',
            
            # Pharma
            'SUNPHARMA', 'CIPLA', 'DRREDDY', 'DIVISLAB', 'BIOCON', 'AUROPHARMA',
            'LUPIN', 'TORNTPHARM', 'ALKEM', 'GLENMARK', 'CADILAHC', 'IPCALAB',
            
            # Steel & Metals
            'TATASTEEL', 'HINDALCO', 'JSWSTEEL', 'VEDL', 'COALINDIA', 'SAIL',
            'NMDC', 'JINDALSTEL', 'HINDZINC', 'NATIONALUM',
            
            # Telecom & Media
            'BHARTIARTL', 'IDEA', 'ZEEL', 'SUNTV', 'HATHWAY', 'DEN',
            
            # Cement & Construction
            'ULTRACEMCO', 'GRASIM', 'AMBUJACEM', 'ACC', 'SHREECEM', 'RAMCOCEM',
            'LT', 'LTTS', 'LTECH',
            
            # Real Estate
            'DLF', 'PHOENIXLTD', 'PRESTIGE', 'SOBHA', 'BRIGADE', 'GODREJPROP',
            
            # Others
            'ADANIENT', 'ADANIPORTS', 'ASIANPAINT', 'TITAN', 'PIDILITIND',
            'HAVELLS', 'VOLTAS', 'BOSCHLTD', 'SIEMENS', 'ABB', 'CROMPTON'
        }
        
        # Auto-detection logic
        if exchange.upper() == "AUTO":
            # First, check if it's a known Indian stock
            if symbol in known_indian_stocks:
                logger.info(f"Detected Indian stock: {symbol}")
                return f"{symbol}.NS"
            
            # Then check if it's in known US stocks list
            if symbol in known_us_stocks:
                logger.info(f"Detected US stock: {symbol}")
                return symbol
            
            # If symbol is 1-4 characters and all uppercase, likely US stock
            # (Most unknown Indian stocks are longer or have specific patterns)
            if len(symbol) <= 4 and symbol.isalpha():
                # Default to US for very short unknown tickers
                logger.info(f"Assuming US stock (short unknown ticker): {symbol}")
                return symbol
            
            # Default to Indian NSE for unknown symbols
            logger.info(f"Defaulting to Indian NSE stock: {symbol}")
            return f"{symbol}.NS"
        
        # Explicit exchange specified
        elif exchange.upper() == "NSE":
            return f"{symbol}.NS"
        elif exchange.upper() == "BSE":
            return f"{symbol}.BO"
        elif exchange.upper() == "US" or exchange.upper() == "NASDAQ" or exchange.upper() == "NYSE":
            return symbol
        else:
            # Default to NSE for unknown exchanges
            return f"{symbol}.NS"


# Create service instance
yahoo_finance_service = YahooFinanceService()
