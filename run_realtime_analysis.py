"""
Real-Time Multi-Model Stock Analysis
Uses live Angel One API data with multi-model orchestrator.
"""
import asyncio
import sys
import os
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.angel_one import AngelOneService
from app.services.multi_model_orchestrator import orchestrator

async def run_realtime_analysis(symbol: str = "RELIANCE-EQ", exchange: str = "NSE"):
    """Run real-time multi-model analysis on live stock data."""
    
    print("\n" + "="*80)
    print("🚀 REAL-TIME MULTI-MODEL STOCK ANALYSIS")
    print("="*80 + "\n")
    
    print(f"📊 Stock: {symbol}")
    print(f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Step 1: Initialize Angel One
    print("🔌 Connecting to Angel One API...")
    try:
        if not AngelOneService._smart_api:
            AngelOneService.initialize()
        print("✅ Angel One connected\n")
    except Exception as e:
        print(f"❌ Angel One connection failed: {str(e)}")
        print("💡 Check your .env credentials\n")
        return
    
    # Step 2: Fetch real-time data
    print("📡 Fetching real-time market data...")
    
    try:
        # Get current price
        current_price = AngelOneService.get_ltp(symbol, exchange)
        if not current_price:
            raise Exception("Could not fetch current price")
        
        print(f"✅ Current Price: ₹{current_price:.2f}\n")
        
        # Get historical data for technical analysis
        print("📈 Fetching historical data...")
        historical_data = AngelOneService.get_historical_data(
            symbol=symbol,
            exchange=exchange,
            interval="ONE_DAY"
        )
        
        if not historical_data or 'data' not in historical_data:
            raise Exception("Could not fetch historical data")
        
        candles = len(historical_data.get('data', []))
        print(f"✅ Historical Data: {candles} candles\n")
        
        # Calculate price change
        data = historical_data['data']
        if len(data) >= 2:
            prev_close = data[-2]['close']
            price_change = ((current_price - prev_close) / prev_close) * 100
        else:
            price_change = 0
        
        print(f"📊 Price Change: {price_change:+.2f}%\n")
        
    except Exception as e:
        print(f"❌ Data fetch failed: {str(e)}\n")
        return
    
    # Step 3: Run Multi-Model Analysis
    print("="*80)
    print("🤖 RUNNING MULTI-MODEL ANALYSIS")
    print("="*80 + "\n")
    
    print("⚡ Analyzing with 4 specialized AI models in parallel...\n")
    
    try:
        result = await orchestrator.analyze_stock_comprehensive(
            symbol=symbol.replace('-EQ', ''),
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
        print(f"   Model Agreement: High" if result['confidence_score'] > 80 else f"   Model Agreement: {'Medium' if result['confidence_score'] > 60 else 'Low'}")
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
        
    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")
        import traceback
        traceback.print_exc()


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Real-time multi-model stock analysis')
    parser.add_argument('--symbol', default='RELIANCE-EQ', help='Stock symbol (default: RELIANCE-EQ)')
    parser.add_argument('--exchange', default='NSE', help='Exchange (default: NSE)')
    
    args = parser.parse_args()
    
    await run_realtime_analysis(args.symbol, args.exchange)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n❌ Analysis interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
