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
    def convert_symbol_to_yahoo(symbol: str, exchange: str = "NSE") -> str:
        """
        Convert Indian stock symbol to Yahoo Finance format.
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE', 'RELIANCE-EQ')
            exchange: Exchange (NSE or BSE)
            
        Returns:
            Yahoo Finance ticker (e.g., 'RELIANCE.NS' or 'RELIANCE.BO')
        """
        # Remove -EQ suffix if present
        symbol = symbol.replace('-EQ', '').strip()
        
        # Add appropriate suffix
        if exchange.upper() == "NSE":
            return f"{symbol}.NS"
        elif exchange.upper() == "BSE":
            return f"{symbol}.BO"
        else:
            return f"{symbol}.NS"  # Default to NSE


# Create service instance
yahoo_finance_service = YahooFinanceService()
