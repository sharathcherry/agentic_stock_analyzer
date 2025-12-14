"""
Example: Stock Watcher with Multi-Model Integration
Shows how to use the new multi-model endpoint instead of single-model.
"""
import asyncio
import httpx
from datetime import datetime
from typing import Dict

# This is an example showing how to modify your existing watcher
# to use the multi-model endpoint instead of single-model


class MultiModelStockWatcher:
    """
    Enhanced Stock Watcher using Multi-Model Analysis.
    
    Changes from original:
    1. Uses /api/get_stock_analysis_multimodel endpoint
    2. Displays model agreement and individual model votes
    3. Shows analysis time and reliability score
    """
    
    def __init__(self, backend_url: str = "http://localhost:8000"):
        self.backend_url = backend_url
        self.watchlist = ["RELIANCE", "TCS", "INFY", "TATAMOTORS"]
        self.previous_prices: Dict[str, float] = {}
        
        # Use multi-model by default, fallback to single-model
        self.use_multi_model = True
        
    async def trigger_analysis(
        self,
        symbol: str,
        trigger_type: str,
        price_change_percent: float
    ):
        """
        Trigger analysis using multi-model or single-model endpoint.
        
        Multi-model provides:
        - Faster analysis (parallel processing)
        - Higher accuracy (consensus from 4 models)
        - Model agreement indicator
        - Individual model votes
        """
        try:
            # Choose endpoint
            if self.use_multi_model:
                endpoint = f"{self.backend_url}/api/get_stock_analysis_multimodel"
                print(f"🚀 Using MULTI-MODEL analysis for {symbol}")
            else:
                endpoint = f"{self.backend_url}/api/get_stock_analysis"
                print(f"🤖 Using single-model analysis for {symbol}")
            
            payload = {
                "symbol": f"{symbol}-EQ",
                "exchange": "NSE",
                "trigger_type": trigger_type,
                "price_change_percent": price_change_percent
            }
            
            print(f"📊 Triggering analysis at {datetime.now().strftime('%H:%M:%S')}...")
            start_time = datetime.now()
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(endpoint, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    analysis_time = (datetime.now() - start_time).total_seconds()
                    
                    # Display results
                    self._display_results(data, analysis_time)
                    
                else:
                    print(f"❌ Analysis failed: {response.status_code}")
                    
                    # Fallback to single model if multi-model fails
                    if self.use_multi_model:
                        print("⚠️  Falling back to single-model...")
                        self.use_multi_model = False
                        await self.trigger_analysis(symbol, trigger_type, price_change_percent)
                        self.use_multi_model = True  # Reset
                        
        except Exception as e:
            print(f"❌ Error: {e}")
            
            # Fallback to single model on error
            if self.use_multi_model:
                print("⚠️  Falling back to single-model...")
                self.use_multi_model = False
                await self.trigger_analysis(symbol, trigger_type, price_change_percent)
                self.use_multi_model = True  # Reset
    
    def _display_results(self, data: Dict, analysis_time: float):
        """Display analysis results with formatting."""
        
        print(f"\n{'='*70}")
        print(f"📈 ANALYSIS RESULTS")
        print(f"{'='*70}")
        
        # Basic Info
        symbol = data.get('symbol', 'N/A')
        current_price = data.get('current_price', 0)
        
        print(f"\n📊 Stock: {symbol}")
        print(f"💰 Current Price: ₹{current_price:.2f}")
        print(f"⏱️  Analysis Time: {analysis_time:.2f}s")
        
        # Decision
        verdict = data.get('verdict', 'N/A')
        confidence = data.get('confidence', 0)
        
        verdict_emoji = {
            'BUY': '🟢',
            'SELL': '🔴',
            'HOLD': '🟡'
        }.get(verdict, '⚪')
        
        print(f"\n{verdict_emoji} VERDICT: {verdict}")
        print(f"🎯 Confidence: {confidence:.1f}%")
        
        # Multi-Model Specific Info
        if 'model_agreement' in data:
            agreement = data.get('model_agreement', 'unknown')
            ensemble_score = data.get('ensemble_score', 0)
            
            agreement_emoji = {
                'strong_consensus': '🟢',
                'moderate_agreement': '🟡',
                'mixed_signals': '🟠'
            }.get(agreement, '⚪')
            
            print(f"\n🤖 MULTI-MODEL ANALYSIS:")
            print(f"   {agreement_emoji} Agreement: {agreement.replace('_', ' ').title()}")
            print(f"   📊 Ensemble Score: {ensemble_score:.1f}/100")
            
            # Model Votes
            if 'model_votes' in data:
                votes = data['model_votes']
                print(f"\n   🗳️  Model Votes:")
                print(f"      • Sentiment: {votes.get('sentiment', 'N/A')}")
                print(f"      • Technical: {votes.get('technical', 'N/A')}")
                print(f"      • Risk: {votes.get('risk', 'N/A')}")
            
            # Individual Model Results (if available)
            if 'sentiment_analysis' in data:
                sentiment = data['sentiment_analysis']
                print(f"\n   💭 Sentiment Model:")
                print(f"      • {sentiment.get('sentiment', 'N/A')} ({sentiment.get('score', 0):.0f}/100)")
                if 'drivers' in sentiment:
                    print(f"      • {sentiment['drivers']}")
            
            if 'technical_analysis' in data:
                technical = data['technical_analysis']
                print(f"\n   📈 Technical Model:")
                print(f"      • {technical.get('signal', 'N/A')} ({technical.get('strength', 0):.0f}/100)")
                if 'patterns' in technical:
                    print(f"      • {technical['patterns']}")
            
            if 'risk_assessment' in data:
                risk = data['risk_assessment']
                print(f"\n   ⚠️  Risk Model:")
                print(f"      • {risk.get('risk_level', 'N/A')} ({risk.get('risk_score', 0):.0f}/100)")
                if 'risk_factors' in risk:
                    print(f"      • {risk['risk_factors']}")
            
            if 'anomaly_detection' in data:
                anomaly = data['anomaly_detection']
                detected = anomaly.get('anomaly_detected', False)
                if detected:
                    print(f"\n   🚨 Anomaly Detected: {anomaly.get('type', 'N/A')}")
                    print(f"      Severity: {anomaly.get('severity', 'N/A')}")
        
        # Price Targets
        target = data.get('target_price', 0)
        stop_loss = data.get('stop_loss', 0)
        
        if target and stop_loss:
            print(f"\n💰 PRICE TARGETS:")
            print(f"   🎯 Target: ₹{target:.2f}")
            print(f"   🛑 Stop Loss: ₹{stop_loss:.2f}")
            
            potential_gain = ((target - current_price) / current_price) * 100
            potential_loss = ((current_price - stop_loss) / current_price) * 100
            
            if potential_loss > 0:
                risk_reward = potential_gain / potential_loss
                print(f"   ⚖️  Risk-Reward: 1:{risk_reward:.2f}")
        
        # Reasoning
        reasoning = data.get('reasoning', '')
        if reasoning:
            print(f"\n💡 REASONING:")
            print(f"   {reasoning}")
        
        # Prediction ID
        prediction_id = data.get('prediction_id', 'N/A')
        print(f"\n🔖 Prediction ID: {prediction_id}")
        
        print(f"\n{'='*70}\n")


async def example_usage():
    """Example showing how to use the multi-model watcher."""
    
    watcher = MultiModelStockWatcher()
    
    # Simulate a price drop alert
    print("🔔 Simulating price drop alert for RELIANCE...")
    await watcher.trigger_analysis(
        symbol="RELIANCE",
        trigger_type="price_drop",
        price_change_percent=-2.5
    )
    
    # Wait a bit
    await asyncio.sleep(2)
    
    # Simulate a price spike alert
    print("\n🔔 Simulating price spike alert for TCS...")
    await watcher.trigger_analysis(
        symbol="TCS",
        trigger_type="price_spike",
        price_change_percent=3.2
    )


async def comparison_example():
    """Example comparing single-model vs multi-model."""
    
    print("\n" + "="*80)
    print("COMPARISON: Single-Model vs Multi-Model")
    print("="*80 + "\n")
    
    watcher = MultiModelStockWatcher()
    
    # Test 1: Single Model
    print("Test 1: Single-Model Analysis")
    print("-" * 80)
    watcher.use_multi_model = False
    await watcher.trigger_analysis("INFY", "price_drop", -1.8)
    
    await asyncio.sleep(2)
    
    # Test 2: Multi Model
    print("\n\nTest 2: Multi-Model Analysis")
    print("-" * 80)
    watcher.use_multi_model = True
    await watcher.trigger_analysis("INFY", "price_drop", -1.8)
    
    print("\n" + "="*80)
    print("📊 Compare the results above!")
    print("Multi-Model should be:")
    print("  ✅ Faster (parallel processing)")
    print("  ✅ More detailed (4 model perspectives)")
    print("  ✅ More reliable (consensus validation)")
    print("="*80 + "\n")


# ============================================================================
# HOW TO INTEGRATE INTO YOUR EXISTING WATCHER
# ============================================================================

"""
INTEGRATION GUIDE:

1. SIMPLE UPDATE (Just change the endpoint):
   
   # In your existing _trigger_analysis method:
   # OLD:
   endpoint = f"{self.backend_url}/api/get_stock_analysis"
   
   # NEW:
   endpoint = f"{self.backend_url}/api/get_stock_analysis_multimodel"


2. ENHANCED UPDATE (Add fallback logic):

   async def _trigger_analysis(self, symbol, trigger_type, price_change_percent):
       try:
           # Try multi-model first
           endpoint = f"{self.backend_url}/api/get_stock_analysis_multimodel"
           response = await client.post(endpoint, json=payload)
           
           if response.status_code == 200:
               data = response.json()
               # Display enhanced results with model votes
               self._display_multi_model_results(data)
           else:
               # Fallback to single model
               endpoint = f"{self.backend_url}/api/get_stock_analysis"
               response = await client.post(endpoint, json=payload)
               # ... handle single model response
       except Exception as e:
           # Fallback to single model on error
           pass


3. DISPLAY MODEL AGREEMENT (Frontend or Watcher):

   agreement = data.get('model_agreement', 'unknown')
   
   if agreement == 'strong_consensus':
       print("🟢 All models agree - High confidence!")
   elif agreement == 'moderate_agreement':
       print("🟡 Most models agree - Medium confidence")
   else:
       print("🟠 Mixed signals - Review carefully")


4. SHOW INDIVIDUAL MODEL VOTES:

   votes = data.get('model_votes', {})
   print(f"Sentiment Model: {votes.get('sentiment')}")
   print(f"Technical Model: {votes.get('technical')}")
   print(f"Risk Model: {votes.get('risk')}")
"""


if __name__ == "__main__":
    print("""
    Multi-Model Stock Watcher Example
    
    This demonstrates how to integrate multi-model analysis into your watcher.
    
    Choose an option:
    1. Run example usage
    2. Run comparison (single vs multi-model)
    """)
    
    choice = input("Enter choice (1 or 2): ")
    
    if choice == "1":
        asyncio.run(example_usage())
    elif choice == "2":
        asyncio.run(comparison_example())
    else:
        print("Invalid choice")
