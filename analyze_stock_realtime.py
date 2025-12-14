"""
Real-Time Multi-Model Stock Analysis with Yahoo Finance
Production-ready script using yfinance for live market data.
Requires Python 3.9+
"""
import asyncio
import sys
import os
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.yahoo_finance import yahoo_finance_service
from app.services.multi_model_orchestrator import orchestrator

async def run_realtime_analysis(symbol: str = "RELIANCE", exchange: str = "NSE"):
    """Run real-time multi-model analysis using Yahoo Finance data."""
    
    print("\n" + "="*80)
    print("🚀 REAL-TIME MULTI-MODEL STOCK ANALYSIS")
    print("="*80 + "\n")
    
    # Convert to Yahoo Finance ticker format
    ticker = yahoo_finance_service.convert_symbol_to_yahoo(symbol, exchange)
    
    print(f"📊 Stock: {symbol} ({ticker})")
    print(f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📡 Data Source: Yahoo Finance (Live Data)\n")
    
    # Fetch real-time data
    print("📡 Fetching live market data from Yahoo Finance...")
    
    try:
        data = yahoo_finance_service.get_stock_data(ticker, period="1mo", interval="1d")
        
        if not data:
            raise Exception("Could not fetch stock data")
        
        current_price = data['current_price']
        previous_close = data['previous_close']
        price_change = data['price_change_percent']
        historical_data = data['historical_data']
        stock_info = data['info']
        
        print(f"✅ {stock_info['name']}")
        print(f"✅ Current Price: ₹{current_price:.2f}")
        print(f"✅ Previous Close: ₹{previous_close:.2f}")
        print(f"📊 Price Change: {price_change:+.2f}%")
        print(f"✅ Historical Data: {len(historical_data['data'])} candles")
        print(f"✅ Volume: {stock_info.get('volume', 'N/A'):,}\n")
        
    except Exception as e:
        print(f"❌ Data fetch failed: {str(e)}\n")
        return
    
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
        print(f"   Stock: {symbol} ({stock_info['name']})")
        print(f"   Price: ₹{current_price:.2f} ({price_change:+.2f}%)")
        print(f"   Recommendation: {verdict_emoji} {final['action']}")
        print(f"   Confidence: {final['confidence']}")
        print(f"   Models Agree: {'Yes ✅' if result['confidence_score'] > 70 else 'Mixed 🟡'}")
        print(f"   Analysis Time: {result['analysis_time_seconds']:.2f}s")
        print(f"   Data Source: Yahoo Finance")
        print()
        
        print("🎯 MULTI-MODEL SYSTEM FEATURES:")
        print("   ✅ 4 specialized AI models analyzed in parallel")
        print("   ✅ Real-time data from Yahoo Finance")
        print("   ✅ Sentiment, Technical, Risk, and Anomaly detection")
        print("   ✅ Ensemble decision from combined insights")
        print("   ✅ Single NVIDIA API key for all models")
        print()
        
    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")
        import traceback
        traceback.print_exc()


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Real-time multi-model stock analysis')
    parser.add_argument('--symbol', default='RELIANCE', help='Stock symbol (default: RELIANCE)')
    parser.add_argument('--exchange', default='NSE', choices=['NSE', 'BSE'], help='Exchange (default: NSE)')
    
    args = parser.parse_args()
    
    print("\n💡 Yahoo Finance Integration (Python 3.9+ Required)")
    print("   NSE stocks: Automatically converted to .NS format")
    print("   BSE stocks: Automatically converted to .BO format")
    print("   Examples: RELIANCE, TCS, INFY, TATAMOTORS\n")
    
    await run_realtime_analysis(args.symbol, args.exchange)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n❌ Analysis interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
