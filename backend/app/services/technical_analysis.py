"""
Technical Analysis Module using ta library.
Calculates indicators like RSI, SMA, EMA, MACD for stock analysis.
"""
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.volatility import BollingerBands
from typing import Dict, Any, List, Optional


class TechnicalAnalysisService:
    """Service for calculating technical indicators."""
    
    @staticmethod
    def calculate_indicators(
        historical_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive technical indicators from historical data.
        
        Args:
            historical_data: List of OHLC data dictionaries
            
        Returns:
            Dictionary containing all calculated indicators
        """
        if not historical_data or len(historical_data) < 20:
            return {
                "error": "Insufficient data for technical analysis (need at least 20 candles)"
            }
        
        # Convert to DataFrame
        df = pd.DataFrame(historical_data)
        
        # Ensure proper data types
        df['close'] = pd.to_numeric(df['close'])
        df['high'] = pd.to_numeric(df['high'])
        df['low'] = pd.to_numeric(df['low'])
        df['open'] = pd.to_numeric(df['open'])
        df['volume'] = pd.to_numeric(df['volume'])
        
        # Calculate indicators
        indicators = {}
        
        # RSI (Relative Strength Index)
        rsi_indicator = RSIIndicator(close=df['close'], window=14)
        df['rsi'] = rsi_indicator.rsi()
        
        indicators['rsi'] = {
            "value": round(df['rsi'].iloc[-1], 2) if not pd.isna(df['rsi'].iloc[-1]) else None,
            "signal": TechnicalAnalysisService._interpret_rsi(df['rsi'].iloc[-1] if not pd.isna(df['rsi'].iloc[-1]) else None)
        }
        
        # Moving Averages
        sma20_indicator = SMAIndicator(close=df['close'], window=20)
        sma50_indicator = SMAIndicator(close=df['close'], window=50)
        df['sma_20'] = sma20_indicator.sma_indicator()
        df['sma_50'] = sma50_indicator.sma_indicator()
        
        current_price = df['close'].iloc[-1]
        sma20 = df['sma_20'].iloc[-1] if not pd.isna(df['sma_20'].iloc[-1]) else None
        sma50 = df['sma_50'].iloc[-1] if not pd.isna(df['sma_50'].iloc[-1]) else None
        
        indicators['sma'] = {
            "sma_20": round(sma20, 2) if sma20 else None,
            "sma_50": round(sma50, 2) if sma50 else None,
            "signal": TechnicalAnalysisService._interpret_sma(current_price, sma20, sma50)
        }
        
        # MACD (Moving Average Convergence Divergence)
        macd_indicator = MACD(close=df['close'])
        df['macd'] = macd_indicator.macd()
        df['macd_signal'] = macd_indicator.macd_signal()
        
        macd = df['macd'].iloc[-1] if not pd.isna(df['macd'].iloc[-1]) else None
        macd_signal = df['macd_signal'].iloc[-1] if not pd.isna(df['macd_signal'].iloc[-1]) else None
        
        indicators['macd'] = {
            "macd": round(macd, 2) if macd else None,
            "signal_line": round(macd_signal, 2) if macd_signal else None,
            "signal": TechnicalAnalysisService._interpret_macd(macd, macd_signal)
        }
        
        # Bollinger Bands
        bollinger = BollingerBands(close=df['close'], window=20, window_dev=2)
        df['bb_upper'] = bollinger.bollinger_hband()
        df['bb_lower'] = bollinger.bollinger_lband()
        
        bb_upper = df['bb_upper'].iloc[-1] if not pd.isna(df['bb_upper'].iloc[-1]) else None
        bb_lower = df['bb_lower'].iloc[-1] if not pd.isna(df['bb_lower'].iloc[-1]) else None
        
        indicators['bollinger_bands'] = {
            "upper": round(bb_upper, 2) if bb_upper else None,
            "lower": round(bb_lower, 2) if bb_lower else None,
            "signal": TechnicalAnalysisService._interpret_bollinger(current_price, bb_upper, bb_lower)
        }
        
        # Volume Analysis
        avg_volume = df['volume'].tail(20).mean()
        current_volume = df['volume'].iloc[-1]
        
        indicators['volume'] = {
            "current": int(current_volume),
            "average_20d": int(avg_volume),
            "signal": "high" if current_volume > avg_volume * 1.5 else "normal"
        }
        
        # Overall Technical Signal
        indicators['overall_signal'] = TechnicalAnalysisService._generate_overall_signal(indicators)
        
        return indicators
    
    @staticmethod
    def _interpret_rsi(rsi: Optional[float]) -> str:
        """Interpret RSI value."""
        if rsi is None:
            return "unknown"
        if rsi > 70:
            return "overbought"
        elif rsi < 30:
            return "oversold"
        else:
            return "neutral"
    
    @staticmethod
    def _interpret_sma(price: float, sma20: Optional[float], sma50: Optional[float]) -> str:
        """Interpret Simple Moving Average signals."""
        if sma20 is None or sma50 is None:
            return "unknown"
        
        if price > sma20 > sma50:
            return "bullish"
        elif price < sma20 < sma50:
            return "bearish"
        else:
            return "neutral"
    
    @staticmethod
    def _interpret_macd(macd: Optional[float], signal: Optional[float]) -> str:
        """Interpret MACD signals."""
        if macd is None or signal is None:
            return "unknown"
        
        if macd > signal:
            return "bullish"
        else:
            return "bearish"
    
    @staticmethod
    def _interpret_bollinger(price: float, upper: Optional[float], lower: Optional[float]) -> str:
        """Interpret Bollinger Bands signals."""
        if upper is None or lower is None:
            return "unknown"
        
        if price >= upper:
            return "overbought"
        elif price <= lower:
            return "oversold"
        else:
            return "neutral"
    
    @staticmethod
    def _generate_overall_signal(indicators: Dict[str, Any]) -> str:
        """
        Generate overall technical signal based on all indicators.
        
        Returns:
            'BUY', 'SELL', or 'HOLD'
        """
        bullish_count = 0
        bearish_count = 0
        
        # RSI
        rsi_signal = indicators.get('rsi', {}).get('signal', 'neutral')
        if rsi_signal == 'oversold':
            bullish_count += 1
        elif rsi_signal == 'overbought':
            bearish_count += 1
        
        # SMA
        sma_signal = indicators.get('sma', {}).get('signal', 'neutral')
        if sma_signal == 'bullish':
            bullish_count += 1
        elif sma_signal == 'bearish':
            bearish_count += 1
        
        # MACD
        macd_signal = indicators.get('macd', {}).get('signal', 'neutral')
        if macd_signal == 'bullish':
            bullish_count += 1
        elif macd_signal == 'bearish':
            bearish_count += 1
        
        # Bollinger Bands
        bb_signal = indicators.get('bollinger_bands', {}).get('signal', 'neutral')
        if bb_signal == 'oversold':
            bullish_count += 1
        elif bb_signal == 'overbought':
            bearish_count += 1
        
        # Decide overall signal
        if bullish_count >= 3:
            return "BUY"
        elif bearish_count >= 3:
            return "SELL"
        else:
            return "HOLD"
