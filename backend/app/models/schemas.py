"""
Pydantic models for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class StockAnalysisRequest(BaseModel):
    """Request model for stock analysis endpoint."""
    symbol: str = Field(..., description="Stock symbol (e.g., TATAMOTORS)")
    exchange: str = Field(default="NSE", description="Exchange (NSE/BSE)")
    trigger_type: Optional[str] = Field(None, description="Type of trigger (price_drop, price_spike, etc.)")
    price_change_percent: Optional[float] = Field(None, description="Price change percentage")


class StockAnalysisResponse(BaseModel):
    """Response model for stock analysis endpoint."""
    symbol: str
    verdict: str
    confidence: float
    explanation: str
    current_price: float
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    risk_level: str
    time_horizon: str
    key_factors: List[str]
    technical_indicators: Dict[str, Any]
    news_sentiment: Dict[str, Any]
    prediction_id: str
    timestamp: str


class WatchlistRequest(BaseModel):
    """Request model for saving user watchlist."""
    user_id: str
    symbols: List[str]
