"""
Stock API Routes - Complete Endpoints for Frontend Support.
Real-time prices, technical indicators, news, charts, and WebSocket.
"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Query
from typing import Optional, List
from datetime import datetime
import asyncio
import json

from app.services.yahoo_finance import YahooFinanceService
from app.services.technical_analysis import TechnicalAnalysisService
from app.services.marketaux import MarketAuxService
from app.services.multi_model_orchestrator import MultiModelOrchestrator
from app.services.firebase_service import FirebaseService


router = APIRouter(prefix="/api", tags=["Stock"])

# Store active WebSocket connections
active_connections: List[WebSocket] = []


@router.get("/stock/{ticker}/realtime")
async def get_realtime_price(ticker: str):
    """
    Get real-time stock data.
    Returns current price, change, volume, OHLC.
    """
    try:
        yahoo_ticker = YahooFinanceService.convert_symbol_to_yahoo(
            ticker.replace('.NS', '').replace('.BO', ''), 
            'NSE'
        )
        
        price_data = YahooFinanceService.get_ltp(yahoo_ticker)
        
        if price_data is None:
            raise HTTPException(status_code=404, detail=f"Could not fetch data for {ticker}")
        
        # Get additional details
        stock_info = YahooFinanceService.get_stock_info(yahoo_ticker)
        
        return {
            "symbol": ticker,
            "price": price_data,
            "change": stock_info.get('change', 0),
            "changePercent": stock_info.get('changePercent', 0),
            "open": stock_info.get('open', 0),
            "high": stock_info.get('high', 0),
            "low": stock_info.get('low', 0),
            "volume": stock_info.get('volume', 0),
            "avgVolume": stock_info.get('avgVolume', 0),
            "marketCap": stock_info.get('marketCap', 0),
            "fiftyTwoWeekHigh": stock_info.get('fiftyTwoWeekHigh', 0),
            "fiftyTwoWeekLow": stock_info.get('fiftyTwoWeekLow', 0),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stock/{ticker}/technical")
async def get_technical_indicators(ticker: str):
    """
    Get all technical indicators for a stock.
    Returns RSI, SMA, MACD, Bollinger Bands, etc.
    """
    try:
        yahoo_ticker = YahooFinanceService.convert_symbol_to_yahoo(
            ticker.replace('.NS', '').replace('.BO', ''), 
            'NSE'
        )
        
        # Get historical data
        historical_data = YahooFinanceService.get_historical_data(yahoo_ticker, days=60)
        
        if not historical_data:
            raise HTTPException(status_code=404, detail="Could not fetch historical data")
        
        # Calculate indicators
        indicators = TechnicalAnalysisService.calculate_indicators(historical_data)
        
        return {
            "symbol": ticker,
            "indicators": indicators,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stock/{ticker}/news")
async def get_stock_news(ticker: str, limit: int = Query(default=10, le=50)):
    """
    Get news articles with sentiment scores.
    """
    try:
        clean_symbol = ticker.replace('.NS', '').replace('.BO', '')
        news_data = await MarketAuxService.fetch_indian_news(
            symbols=[clean_symbol],
            limit=limit
        )
        
        return {
            "symbol": ticker,
            "news": news_data.get('data', []),
            "aggregate_sentiment": news_data.get('aggregate_sentiment', {}),
            "total": len(news_data.get('data', [])),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stock/{ticker}/chart")
async def get_chart_data(
    ticker: str, 
    period: str = Query(default="1M", regex="^(1D|1W|1M|3M|1Y)$")
):
    """
    Get OHLC data for charting.
    Supports periods: 1D, 1W, 1M, 3M, 1Y
    """
    try:
        days_map = {'1D': 1, '1W': 7, '1M': 30, '3M': 90, '1Y': 365}
        days = days_map.get(period, 30)
        
        yahoo_ticker = YahooFinanceService.convert_symbol_to_yahoo(
            ticker.replace('.NS', '').replace('.BO', ''), 
            'NSE'
        )
        
        historical_data = YahooFinanceService.get_historical_data(yahoo_ticker, days=days)
        
        if not historical_data:
            raise HTTPException(status_code=404, detail="Could not fetch chart data")
        
        # Format for chart library
        chart_data = []
        for item in historical_data:
            chart_data.append({
                "timestamp": item.get('date'),
                "open": item.get('open'),
                "high": item.get('high'),
                "low": item.get('low'),
                "close": item.get('close'),
                "volume": item.get('volume')
            })
        
        return {
            "symbol": ticker,
            "period": period,
            "data": chart_data,
            "count": len(chart_data),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stock/{ticker}/analyze")
async def trigger_analysis(ticker: str):
    """
    Trigger AI multi-model analysis for a stock.
    """
    try:
        clean_symbol = ticker.replace('.NS', '').replace('.BO', '')
        
        orchestrator = MultiModelOrchestrator()
        result = await orchestrator.analyze(symbol=clean_symbol, exchange='NSE')
        
        # Save prediction to Firebase
        try:
            FirebaseService.save_prediction(result)
        except Exception as e:
            print(f"Warning: Could not save prediction to Firebase: {e}")
        
        return {
            "symbol": ticker,
            "analysis": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predictions/{ticker}")
async def get_prediction_history(
    ticker: str, 
    limit: int = Query(default=50, le=100)
):
    """
    Get prediction history for a stock.
    """
    try:
        clean_symbol = ticker.replace('.NS', '').replace('.BO', '')
        
        predictions = FirebaseService.get_predictions(
            symbol=clean_symbol,
            limit=limit
        )
        
        return {
            "symbol": ticker,
            "predictions": predictions,
            "count": len(predictions),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        # Return empty list if Firebase not configured
        return {
            "symbol": ticker,
            "predictions": [],
            "count": 0,
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/watchlist")
async def get_watchlist():
    """
    Get user's stock watchlist.
    """
    # Default watchlist - can be extended with user authentication
    default_watchlist = [
        {"ticker": "RELIANCE.NS", "name": "Reliance Industries"},
        {"ticker": "TCS.NS", "name": "Tata Consultancy Services"},
        {"ticker": "INFY.NS", "name": "Infosys"},
        {"ticker": "HDFCBANK.NS", "name": "HDFC Bank"},
        {"ticker": "ICICIBANK.NS", "name": "ICICI Bank"},
    ]
    
    return {
        "watchlist": default_watchlist,
        "count": len(default_watchlist),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/stock/price/{ticker}")
async def get_stock_price(ticker: str):
    """
    Simple endpoint to get current stock price.
    Used by frontend for quick price updates.
    """
    try:
        yahoo_ticker = YahooFinanceService.convert_symbol_to_yahoo(
            ticker.replace('.NS', '').replace('.BO', ''), 
            'NSE'
        )
        
        price = YahooFinanceService.get_ltp(yahoo_ticker)
        stock_info = YahooFinanceService.get_stock_info(yahoo_ticker)
        
        return {
            "ticker": ticker,
            "price": price,
            "change": stock_info.get('change', 0),
            "changePercent": stock_info.get('changePercent', 0),
            "open": stock_info.get('open', 0),
            "high": stock_info.get('high', 0),
            "low": stock_info.get('low', 0),
            "volume": stock_info.get('volume', 0)
        }
    except Exception as e:
        return {"ticker": ticker, "price": None, "error": str(e)}


# WebSocket endpoint for live prices
@router.websocket("/ws/prices")
async def websocket_prices(websocket: WebSocket):
    """
    WebSocket endpoint for real-time price updates.
    Clients can subscribe to specific tickers.
    """
    await websocket.accept()
    active_connections.append(websocket)
    
    subscribed_tickers = set()
    
    try:
        while True:
            # Receive messages (subscribe/unsubscribe commands)
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=5.0)
                message = json.loads(data)
                
                if message.get('action') == 'subscribe':
                    ticker = message.get('ticker')
                    if ticker:
                        subscribed_tickers.add(ticker)
                        await websocket.send_json({
                            "type": "subscribed",
                            "ticker": ticker
                        })
                
                elif message.get('action') == 'unsubscribe':
                    ticker = message.get('ticker')
                    subscribed_tickers.discard(ticker)
                    await websocket.send_json({
                        "type": "unsubscribed",
                        "ticker": ticker
                    })
                    
            except asyncio.TimeoutError:
                pass  # No message received, continue to send updates
            
            # Send price updates for subscribed tickers
            for ticker in subscribed_tickers:
                try:
                    yahoo_ticker = YahooFinanceService.convert_symbol_to_yahoo(
                        ticker.replace('.NS', '').replace('.BO', ''), 
                        'NSE'
                    )
                    price = YahooFinanceService.get_ltp(yahoo_ticker)
                    stock_info = YahooFinanceService.get_stock_info(yahoo_ticker)
                    
                    await websocket.send_json({
                        "type": "price_update",
                        "ticker": ticker,
                        "price": price,
                        "change": stock_info.get('change', 0),
                        "changePercent": stock_info.get('changePercent', 0),
                        "timestamp": datetime.utcnow().isoformat()
                    })
                except Exception as e:
                    print(f"Error fetching price for {ticker}: {e}")
            
            # Small delay between updates
            await asyncio.sleep(2)
            
    except WebSocketDisconnect:
        active_connections.remove(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)
