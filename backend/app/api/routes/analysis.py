"""
Stock Analysis API Routes.
Main endpoint for triggering AI-powered stock analysis.
Supports both single-model and multi-model analysis approaches.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
from datetime import datetime

from app.models.schemas import StockAnalysisRequest, StockAnalysisResponse
from app.services.yahoo_finance import yahoo_finance_service
from app.services.marketaux import MarketAuxService
from app.services.technical_analysis import TechnicalAnalysisService
from app.services.ai_agent import ai_agent
from app.services.multi_model_orchestrator import orchestrator
from app.services.firebase_service import FirebaseService

router = APIRouter(prefix="/api", tags=["analysis"])


@router.post("/get_stock_analysis", response_model=StockAnalysisResponse)
async def get_stock_analysis(request: StockAnalysisRequest):
    """
    Main endpoint for stock analysis.
    Called by the Watcher script when a trigger condition is met.
    
    Flow:
    1. Fetch current price from Angel One
    2. Fetch historical data for technical analysis
    3. Fetch news and sentiment from MarketAux
    4. Run AI agent analysis
    5. Save prediction to Firestore
    6. Return analysis result
    """
    try:
        symbol = request.symbol
        exchange = request.exchange
        
        # Step 1: Get current price
        current_price = AngelOneService.get_ltp(symbol, exchange)
        if current_price is None:
            raise HTTPException(status_code=400, detail=f"Unable to fetch price for {symbol}")
        
        # Step 2: Get historical data for technical analysis
        historical_data = AngelOneService.get_historical_data(
            symbol=symbol,
            exchange=exchange,
            interval="ONE_DAY"
        )
        
        if not historical_data:
            raise HTTPException(status_code=400, detail=f"Unable to fetch historical data for {symbol}")
        
        # Step 3: Calculate technical indicators
        technical_indicators = TechnicalAnalysisService.calculate_indicators(historical_data)
        
        # Step 4: Fetch news and sentiment
        news_data = await MarketAuxService.fetch_indian_news(symbols=[symbol], limit=10)
        
        # Step 5: Run AI agent analysis
        ai_analysis = await ai_agent.analyze_stock(
            symbol=symbol,
            current_price=current_price,
            technical_indicators=technical_indicators,
            news_data=news_data,
            price_change_percent=request.price_change_percent
        )
        
        # Step 6: Save prediction to Firestore
        prediction_data = {
            "verdict": ai_analysis.get("verdict", "HOLD"),
            "explanation": ai_analysis.get("explanation", ""),
            "confidence": ai_analysis.get("confidence", 0.0),
            "current_price": current_price,
            "target_price": ai_analysis.get("target_price"),
            "technical_indicators": technical_indicators,
            "news_sentiment": news_data.get("aggregate_sentiment", {}),
            "ai_reasoning": ai_analysis.get("key_factors", []),
        }
        
        prediction_id = FirebaseService.save_prediction(symbol, prediction_data)
        
        # Step 7: Build response
        response = StockAnalysisResponse(
            symbol=symbol,
            verdict=ai_analysis.get("verdict", "HOLD"),
            confidence=ai_analysis.get("confidence", 0.0),
            explanation=ai_analysis.get("explanation", ""),
            current_price=current_price,
            target_price=ai_analysis.get("target_price"),
            stop_loss=ai_analysis.get("stop_loss"),
            risk_level=ai_analysis.get("risk_level", "MEDIUM"),
            time_horizon=ai_analysis.get("time_horizon", "SHORT_TERM"),
            key_factors=ai_analysis.get("key_factors", []),
            technical_indicators=technical_indicators,
            news_sentiment=news_data.get("aggregate_sentiment", {}),
            prediction_id=prediction_id,
            timestamp=datetime.utcnow().isoformat()
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")


@router.post("/get_stock_analysis_multimodel", response_model=Dict[str, Any])
async def get_stock_analysis_multimodel(request: StockAnalysisRequest):
    """
    Multi-Model Stock Analysis Endpoint.
    Uses multiple specialized AI models for different tasks to provide
    more reliable and efficient results.
    
    Architecture:
    - Sentiment Analysis: Fast Llama 70B
    - Technical Analysis: Mistral 8x7B
    - Risk Assessment: Advanced Llama 405B
    - Anomaly Detection: Fast Llama 70B
    - Final Decision: Ensemble of all models
    
    Flow:
    1. Fetch current price and historical data
    2. Run sentiment, technical, risk, and anomaly models in parallel
    3. Combine results using ensemble approach
    4. Save prediction to Firestore
    5. Return comprehensive multi-model analysis
    """
    try:
        symbol = request.symbol
        exchange = request.exchange
        
        # Step 1: Get current price
        current_price = AngelOneService.get_ltp(symbol, exchange)
        if current_price is None:
            raise HTTPException(status_code=400, detail=f"Unable to fetch price for {symbol}")
        
        # Step 2: Get historical data for technical analysis
        historical_data = AngelOneService.get_historical_data(
            symbol=symbol,
            exchange=exchange,
            interval="ONE_DAY"
        )
        
        if not historical_data:
            raise HTTPException(status_code=400, detail=f"Unable to fetch historical data for {symbol}")
        
        # Step 3: Run multi-model orchestrator (models run in parallel)
        multi_model_analysis = await orchestrator.analyze_stock_comprehensive(
            symbol=symbol,
            current_price=current_price,
            historical_data=historical_data,
            price_change_percent=request.price_change_percent
        )
        
        # Step 4: Save prediction to Firestore
        final_decision = multi_model_analysis.get("final_decision", {})
        prediction_data = {
            "verdict": final_decision.get("action", "HOLD"),
            "explanation": final_decision.get("reasoning", ""),
            "confidence": multi_model_analysis.get("confidence_score", 0.0),
            "current_price": current_price,
            "target_price": final_decision.get("target_price"),
            "stop_loss": final_decision.get("stop_loss"),
            "ensemble_score": final_decision.get("ensemble_score"),
            "models_used": multi_model_analysis.get("models_used", {}),
            "sentiment_analysis": multi_model_analysis.get("sentiment_analysis", {}),
            "technical_analysis": multi_model_analysis.get("technical_analysis", {}),
            "risk_assessment": multi_model_analysis.get("risk_assessment", {}),
            "anomaly_detection": multi_model_analysis.get("anomaly_detection", {}),
            "analysis_time": multi_model_analysis.get("analysis_time_seconds", 0),
            "model_type": "multi_model_ensemble"
        }
        
        prediction_id = FirebaseService.save_prediction(symbol, prediction_data)
        
        # Step 5: Build comprehensive response
        response = {
            "symbol": symbol,
            "prediction_id": prediction_id,
            "timestamp": multi_model_analysis.get("timestamp"),
            "analysis_type": "multi_model_ensemble",
            "analysis_time_seconds": multi_model_analysis.get("analysis_time_seconds"),
            
            # Final Decision
            "verdict": final_decision.get("action", "HOLD"),
            "confidence": multi_model_analysis.get("confidence_score", 0.0),
            "ensemble_score": final_decision.get("ensemble_score"),
            "reasoning": final_decision.get("reasoning", ""),
            
            # Price Targets
            "current_price": current_price,
            "target_price": final_decision.get("target_price"),
            "stop_loss": final_decision.get("stop_loss"),
            
            # Individual Model Results
            "model_votes": final_decision.get("model_votes", {}),
            "sentiment_analysis": multi_model_analysis.get("sentiment_analysis", {}),
            "technical_analysis": multi_model_analysis.get("technical_analysis", {}),
            "risk_assessment": multi_model_analysis.get("risk_assessment", {}),
            "anomaly_detection": multi_model_analysis.get("anomaly_detection", {}),
            
            # Metadata
            "models_used": multi_model_analysis.get("models_used", {}),
            "technical_indicators": multi_model_analysis.get("metadata", {}).get("technical_indicators", {}),
            "news_count": multi_model_analysis.get("metadata", {}).get("news_count", 0),
            
            # Performance Metrics
            "reliability_score": multi_model_analysis.get("confidence_score", 0.0),
            "model_agreement": self._calculate_model_agreement(multi_model_analysis)
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multi-model analysis error: {str(e)}")


def _calculate_model_agreement(analysis: Dict[str, Any]) -> str:
    """Calculate agreement between models."""
    try:
        votes = analysis.get("final_decision", {}).get("model_votes", {})
        
        # Extract actions from each model
        sentiment = votes.get("sentiment", "neutral")
        technical = votes.get("technical", "hold")
        risk = votes.get("risk", "medium")
        
        # Map to buy/sell/hold
        buy_votes = 0
        sell_votes = 0
        hold_votes = 0
        
        if sentiment in ["bullish", "positive"]:
            buy_votes += 1
        elif sentiment in ["bearish", "negative"]:
            sell_votes += 1
        else:
            hold_votes += 1
        
        if technical == "buy":
            buy_votes += 1
        elif technical == "sell":
            sell_votes += 1
        else:
            hold_votes += 1
        
        if risk in ["low"]:
            buy_votes += 0.5
        elif risk in ["high", "extreme"]:
            sell_votes += 0.5
        
        max_votes = max(buy_votes, sell_votes, hold_votes)
        total_votes = buy_votes + sell_votes + hold_votes
        
        if total_votes == 0:
            return "unknown"
        
        agreement_percent = (max_votes / total_votes) * 100
        
        if agreement_percent >= 80:
            return "strong_consensus"
        elif agreement_percent >= 60:
            return "moderate_agreement"
        else:
            return "mixed_signals"
    except:
        return "unknown"



@router.get("/predictions/{symbol}")
async def get_predictions(symbol: str, limit: int = 50):
    """Get historical predictions for a symbol."""
    try:
        predictions = FirebaseService.get_predictions(symbol=symbol, limit=limit)
        return {
            "symbol": symbol,
            "predictions": predictions,
            "count": len(predictions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching predictions: {str(e)}")


@router.get("/predictions")
async def get_all_predictions(limit: int = 100, status: str = None):
    """Get all predictions with optional status filter."""
    try:
        predictions = FirebaseService.get_predictions(limit=limit, status=status)
        return {
            "predictions": predictions,
            "count": len(predictions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching predictions: {str(e)}")
