"""
24/7 Stock Watcher Script.
Monitors Angel One WebSocket for price anomalies and triggers analysis.
"""
import asyncio
import websocket
import json
import httpx
from datetime import datetime
from typing import Dict, List
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.services.angel_one import AngelOneService


class StockWatcher:
    """Watches stocks via WebSocket and triggers analysis on anomalies."""
    
    def __init__(self):
        self.backend_url = settings.BACKEND_URL
        self.watchlist = settings.watchlist_symbols_list
        self.price_drop_threshold = settings.PRICE_DROP_THRESHOLD
        self.price_spike_threshold = settings.PRICE_SPIKE_THRESHOLD
        self.previous_prices: Dict[str, float] = {}
        self.ws = None
        
    async def start_monitoring(self):
        """Start the WebSocket monitoring loop."""
        print("🚀 Stock Watcher Starting...")
        print(f"📊 Monitoring symbols: {', '.join(self.watchlist)}")
        print(f"📉 Price drop threshold: {self.price_drop_threshold}%")
        print(f"📈 Price spike threshold: {self.price_spike_threshold}%")
        
        # Initialize previous prices
        await self._initialize_prices()
        
        # Start monitoring loop
        while True:
            try:
                await self._check_prices()
                await asyncio.sleep(5)  # Check every 5 seconds
            except KeyboardInterrupt:
                print("\n⛔ Stopping watcher...")
                break
            except Exception as e:
                print(f"❌ Error in monitoring loop: {e}")
                await asyncio.sleep(10)  # Wait before retrying
    
    async def _initialize_prices(self):
        """Initialize baseline prices for watchlist symbols."""
        print("🔄 Initializing baseline prices...")
        
        for symbol in self.watchlist:
            try:
                price = AngelOneService.get_ltp(f"{symbol}-EQ", "NSE")
                if price:
                    self.previous_prices[symbol] = price
                    print(f"  ✓ {symbol}: ₹{price:.2f}")
            except Exception as e:
                print(f"  ✗ Error fetching {symbol}: {e}")
        
        print(f"✅ Initialized {len(self.previous_prices)} symbols\n")
    
    async def _check_prices(self):
        """Check current prices and detect anomalies."""
        for symbol in self.watchlist:
            try:
                current_price = AngelOneService.get_ltp(f"{symbol}-EQ", "NSE")
                
                if not current_price or symbol not in self.previous_prices:
                    continue
                
                previous_price = self.previous_prices[symbol]
                price_change_percent = ((current_price - previous_price) / previous_price) * 100
                
                # Check for anomalies
                trigger_type = None
                
                if price_change_percent <= -self.price_drop_threshold:
                    trigger_type = "price_drop"
                    print(f"\n🔴 ALERT: {symbol} dropped {price_change_percent:.2f}%")
                    print(f"   Previous: ₹{previous_price:.2f} → Current: ₹{current_price:.2f}")
                    
                elif price_change_percent >= self.price_spike_threshold:
                    trigger_type = "price_spike"
                    print(f"\n🟢 ALERT: {symbol} spiked {price_change_percent:.2f}%")
                    print(f"   Previous: ₹{previous_price:.2f} → Current: ₹{current_price:.2f}")
                
                # Trigger analysis if anomaly detected
                if trigger_type:
                    await self._trigger_analysis(symbol, trigger_type, price_change_percent)
                    # Update baseline after triggering
                    self.previous_prices[symbol] = current_price
                
            except Exception as e:
                print(f"❌ Error checking {symbol}: {e}")
    
    async def _trigger_analysis(self, symbol: str, trigger_type: str, price_change_percent: float):
        """Trigger backend analysis endpoint."""
        try:
            endpoint = f"{self.backend_url}/api/get_stock_analysis"
            
            payload = {
                "symbol": f"{symbol}-EQ",
                "exchange": "NSE",
                "trigger_type": trigger_type,
                "price_change_percent": price_change_percent
            }
            
            print(f"🤖 Triggering AI analysis for {symbol}...")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(endpoint, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Analysis complete:")
                    print(f"   Verdict: {data.get('verdict')} (Confidence: {data.get('confidence'):.2f})")
                    print(f"   Explanation: {data.get('explanation')}")
                    print(f"   Prediction ID: {data.get('prediction_id')}\n")
                else:
                    print(f"❌ Analysis failed: {response.status_code} - {response.text}\n")
                    
        except Exception as e:
            print(f"❌ Error triggering analysis: {e}\n")


async def main():
    """Main entry point."""
    # Ensure Angel One is initialized
    if not AngelOneService._smart_api:
        print("Initializing Angel One connection...")
        AngelOneService.initialize()
    
    watcher = StockWatcher()
    await watcher.start_monitoring()


if __name__ == "__main__":
    asyncio.run(main())
