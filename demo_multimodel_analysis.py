"""
Real-Time Multi-Model Stock Analysis (Demo with Mock Data)
Demonstrates the multi-model system without requiring Angel One API.
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta
import random

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.multi_model_orchestrator import orchestrator

def generate_mock_historical_data(days=30):
    """Generate realistic mock historical data."""
    data = []
    base_price = 2450
    
    for i in range(days):
        # Simulate realistic price movement
        change = random.uniform(-0.02, 0.02)  # ±2% daily change
        base_price = base_price * (1 + change)
        
        open_price = base_price + random.uniform(-10, 10)
        high = max(open_price, base_price) + random.uniform(0, 15)
        low = min(open_price, base_price) - random.uniform(0, 15)
        close = base_price
        volume = random.randint(800000, 1500000)
        
        data.append({
            'timestamp': (datetime.now() - timedelta(days=days-i)).isoformat(),
            'open': round(open_price, 2),
            'high': round(high, 2),
            'low': round(low, 2),
            'close': round(close, 2),
            'volume': volume
        })
    
    return {'data': data}

async def run_demo_analysis(symbol: str = "RELIANCE"):
    """Run demo analysis with mock data."""
    
    print("\n" + "="*80)
    print("🚀 REAL-TIME MULTI-MODEL STOCK ANALYSIS (DEMO)")
    print("="*80 + "\n")
    
    print("💡 Note: Using simulated market data for demonstration\n")
    
    print(f"📊 Stock: {symbol}")
    print(f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Generate mock data
    print("📡 Generating realistic market data...")
    historical_data = generate_mock_historical_data(30)
    
    current_price = historical_data['data'][-1]['close']
    prev_price = historical_data['data'][-2]['close']
    price_change = ((current_price - prev_price) / prev_price) * 100
    
    print(f"✅ Current Price: ₹{current_price:.2f}")
    print(f"✅ Historical Data: 30 candles")
    print(f"📊 Price Change: {price_change:+.2f}%\n")
    
    # Run Multi-Model Analysis
    print("="*80)
    print("🤖 RUNNING MULTI-MODEL ANALYSIS")
    print("="*80 + "\n")
    
    print("⚡ Analyzing with 4 specialized AI models in parallel...\n")
    
    try:
        result = await orchestrator.analyze_stock_comprehensive(
            symbol=symbol,
            current_price=current_price,
            historical_data=historical_data,
            price_change_percent=price_change
        )
        
        # Display Results
        print("="*80)
        print("✅ ANALYSIS COMPLETE!")
        print("="*80 + "\n")
        
        print(f"⏱️  Analysis Time: {result['analysis_time_seconds']:.2f} seconds\n")
        
        # Models Used
        print("🤖 MODELS USED:")
        for task, model in result['models_used'].items():
            print(f"   • {task.title()}: {model}")
        print()
        
        # Final Decision
        final = result['final_decision']
        verdict_emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(final['action'], "⚪")
        
        print("="*80)
        print(f"📊 FINAL DECISION: {verdict_emoji} {final['action']}")
        print("="*80 + "\n")
        
        print(f"🎯 Confidence: {final['confidence']}")
        print(f"💯 Ensemble Score: {final['ensemble_score']:.1f}/100")
        print(f"💡 Reasoning: {final['reasoning']}\n")
        
        # Model Votes
        print("🗳️  MODEL VOTES:")
        votes = final['model_votes']
        print(f"   💭 Sentiment Model: {votes['sentiment']}")
        print(f"   📈 Technical Model: {votes['technical']}")
        print(f"   ⚠️  Risk Model: {votes['risk']}\n")
        
        # Price Targets
        print("💰 PRICE TARGETS:")
        print(f"   🎯 Target Price: ₹{final['target_price']:.2f}")
        print(f"   🛑 Stop Loss: ₹{final['stop_loss']:.2f}")
        
        gain = ((final['target_price'] - current_price) / current_price) * 100
        loss = ((current_price - final['stop_loss']) / current_price) * 100
        if loss > 0:
            rr = gain / loss
            print(f"   ⚖️  Risk-Reward: 1:{rr:.2f}\n")
        
        # Individual Model Results
        print("="*80)
        print("🔍 DETAILED MODEL ANALYSIS")
        print("="*80 + "\n")
        
        # Sentiment
        sentiment = result.get('sentiment_analysis', {})
        if 'error' not in sentiment:
            print("💭 SENTIMENT ANALYSIS:")
            print(f"   Sentiment: {sentiment.get('sentiment', 'N/A').title()}")
            print(f"   Score: {sentiment.get('score', 0):.0f}/100")
            if 'drivers' in sentiment:
                print(f"   Drivers: {sentiment['drivers']}")
            if 'mood' in sentiment:
                print(f"   Market Mood: {sentiment['mood']}")
            print()
        
        # Technical
        technical = result.get('technical_analysis', {})
        if 'error' not in technical:
            print("📈 TECHNICAL ANALYSIS:")
            print(f"   Signal: {technical.get('signal', 'N/A').upper()}")
            print(f"   Strength: {technical.get('strength', 0):.0f}/100")
            if 'key_indicators' in technical:
                print(f"   Key Indicators: {technical['key_indicators']}")
            if 'patterns' in technical:
                print(f"   Patterns: {technical['patterns']}")
            print()
        
        # Risk
        risk = result.get('risk_assessment', {})
        if 'error' not in risk:
            print("⚠️  RISK ASSESSMENT:")
            print(f"   Risk Level: {risk.get('risk_level', 'N/A').upper()}")
            print(f"   Risk Score: {risk.get('risk_score', 0):.0f}/100")
            if 'risk_factors' in risk:
                print(f"   Risk Factors: {risk['risk_factors']}")
            if 'downside' in risk:
                print(f"   Downside: {risk['downside']}")
            print()
        
        # Anomaly
        anomaly = result.get('anomaly_detection', {})
        detected = anomaly.get('anomaly_detected', False)
        print("🔍 ANOMALY DETECTION:")
        if detected:
            print(f"   ⚠️  ANOMALY DETECTED!")
            print(f"   Type: {anomaly.get('type', 'N/A')}")
            print(f"   Severity: {anomaly.get('severity', 'N/A')}")
            print(f"   Reason: {anomaly.get('reason', 'N/A')}")
        else:
            print(f"   ✅ No anomalies detected")
        print()
        
        # Confidence Metrics
        print("="*80)
        print("📊 RELIABILITY METRICS")
        print("="*80 + "\n")
        print(f"   Overall Confidence: {result['confidence_score']:.1f}%")
        agreement = "High" if result['confidence_score'] > 80 else ("Medium" if result['confidence_score'] > 60 else "Low")
        print(f"   Model Agreement: {agreement}")
        print()
        
        # Summary
        print("="*80)
        print("✅ REAL-TIME ANALYSIS COMPLETE")
        print("="*80 + "\n")
        
        print("💡 SUMMARY:")
        print(f"   Stock: {symbol}")
        print(f"   Price: ₹{current_price:.2f} ({price_change:+.2f}%)")
        print(f"   Recommendation: {verdict_emoji} {final['action']}")
        print(f"   Confidence: {final['confidence']}")
        print(f"   Models Agree: {'Yes ✅' if result['confidence_score'] > 70 else 'Mixed 🟡'}")
        print(f"   Analysis Time: {result['analysis_time_seconds']:.2f}s")
        print()
        
        print("🎯 WHAT JUST HAPPENED:")
        print("   ✅ 4 specialized AI models analyzed the stock in parallel")
        print("   ✅ Each model provided expert analysis in its domain")
        print("   ✅ Ensemble engine combined all insights")
        print("   ✅ Final decision based on consensus")
        print()
        
        print("📝 TO USE WITH REAL DATA:")
        print("   1. Fix your Angel One TOTP secret in .env")
        print("   2. Run: python run_realtime_analysis.py")
        print("   3. Or use the API endpoint: POST /api/get_stock_analysis_multimodel")
        print()
        
    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        asyncio.run(run_demo_analysis("RELIANCE"))
    except KeyboardInterrupt:
        print("\n\n❌ Analysis interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
