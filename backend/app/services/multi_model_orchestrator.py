"""
Multi-Model Orchestrator Service
Coordinates multiple AI models for different tasks to provide reliable and efficient results.

Architecture:
1. News Sentiment Analysis → Fast, lightweight model (Llama 3.1 70B)
2. Technical Analysis Interpretation → Medium model (Mistral 8x7B)
3. Risk Assessment → Specialized model (Llama 3.1 405B)
4. Final Trading Decision → Ensemble of all models
5. Market Anomaly Detection → Real-time lightweight model
"""

from typing import Dict, Any, Optional, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.config import settings
from app.services.marketaux import MarketAuxService
from app.services.technical_analysis import TechnicalAnalysisService
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ModelConfig:
    """Configuration for different specialized models."""
    
    # Fast model for quick sentiment analysis
    SENTIMENT_MODEL = "meta/llama-3.1-70b-instruct"
    
    # Medium model for technical interpretation
    TECHNICAL_MODEL = "mistralai/mixtral-8x7b-instruct-v0.1"
    
    # Advanced model for risk assessment and complex reasoning
    RISK_MODEL = "meta/llama-3.1-405b-instruct"
    
    # Fast model for anomaly detection
    ANOMALY_MODEL = "meta/llama-3.1-70b-instruct"
    
    # Model temperatures for different tasks
    TEMPERATURES = {
        "sentiment": 0.3,  # Low temperature for factual analysis
        "technical": 0.5,  # Medium for pattern recognition
        "risk": 0.7,       # Higher for creative risk scenarios
        "anomaly": 0.2,    # Very low for precise detection
    }


class MultiModelOrchestrator:
    """
    Orchestrates multiple AI models for comprehensive stock analysis.
    Each model specializes in a specific task for optimal performance.
    """
    
    def __init__(self):
        """Initialize multiple specialized models."""
        logger.info("Initializing Multi-Model Orchestrator")
        
        # Sentiment Analysis Model (Fast)
        self.sentiment_model = ChatOpenAI(
            model=ModelConfig.SENTIMENT_MODEL,
            temperature=ModelConfig.TEMPERATURES["sentiment"],
            base_url=settings.NVIDIA_BASE_URL,
            api_key=settings.NVIDIA_API_KEY
        )
        
        # Technical Analysis Model (Medium)
        self.technical_model = ChatOpenAI(
            model=ModelConfig.TECHNICAL_MODEL,
            temperature=ModelConfig.TEMPERATURES["technical"],
            base_url=settings.NVIDIA_BASE_URL,
            api_key=settings.NVIDIA_API_KEY
        )
        
        # Risk Assessment Model (Advanced)
        self.risk_model = ChatOpenAI(
            model=ModelConfig.RISK_MODEL,
            temperature=ModelConfig.TEMPERATURES["risk"],
            base_url=settings.NVIDIA_BASE_URL,
            api_key=settings.NVIDIA_API_KEY
        )
        
        # Anomaly Detection Model (Fast)
        self.anomaly_model = ChatOpenAI(
            model=ModelConfig.ANOMALY_MODEL,
            temperature=ModelConfig.TEMPERATURES["anomaly"],
            base_url=settings.NVIDIA_BASE_URL,
            api_key=settings.NVIDIA_API_KEY
        )
        
        # Initialize services
        self.news_service = MarketAuxService()
        self.technical_service = TechnicalAnalysisService()
        
        logger.info("Multi-Model Orchestrator initialized successfully")
    
    async def analyze_stock_comprehensive(
        self,
        symbol: str,
        current_price: float,
        historical_data: Optional[Dict] = None,
        price_change_percent: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive multi-model stock analysis.
        Each task is delegated to the most appropriate model.
        
        Args:
            symbol: Stock symbol
            current_price: Current trading price
            historical_data: Historical price data
            price_change_percent: Recent price change percentage
            
        Returns:
            Comprehensive analysis with insights from all models
        """
        try:
            logger.info(f"Starting multi-model analysis for {symbol}")
            start_time = datetime.now()
            
            # Step 1: Gather data (parallel)
            news_data, technical_indicators = await asyncio.gather(
                self._fetch_news_async(symbol),
                self._fetch_technical_async(symbol, historical_data)
            )
            
            # Step 2: Run specialized models in parallel
            sentiment_task = self._analyze_sentiment(symbol, news_data)
            technical_task = self._analyze_technical(symbol, current_price, technical_indicators)
            risk_task = self._assess_risk(symbol, current_price, technical_indicators, news_data, price_change_percent)
            
            sentiment_result, technical_result, risk_result = await asyncio.gather(
                sentiment_task,
                technical_task,
                risk_task,
                return_exceptions=True
            )
            
            # Handle any failures gracefully
            sentiment_result = self._handle_result(sentiment_result, "Sentiment analysis unavailable")
            technical_result = self._handle_result(technical_result, "Technical analysis unavailable")
            risk_result = self._handle_result(risk_result, "Risk assessment unavailable")
            
            # Step 3: Ensemble decision (combine all insights)
            final_decision = await self._generate_ensemble_decision(
                symbol=symbol,
                current_price=current_price,
                sentiment=sentiment_result,
                technical=technical_result,
                risk=risk_result,
                price_change_percent=price_change_percent
            )
            
            # Step 4: Check for anomalies
            anomaly_check = await self._detect_anomaly(
                symbol=symbol,
                current_price=current_price,
                price_change_percent=price_change_percent,
                technical_indicators=technical_indicators
            )
            
            analysis_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "symbol": symbol,
                "current_price": current_price,
                "timestamp": datetime.now().isoformat(),
                "analysis_time_seconds": analysis_time,
                "models_used": {
                    "sentiment": ModelConfig.SENTIMENT_MODEL,
                    "technical": ModelConfig.TECHNICAL_MODEL,
                    "risk": ModelConfig.RISK_MODEL,
                    "anomaly": ModelConfig.ANOMALY_MODEL
                },
                "sentiment_analysis": sentiment_result,
                "technical_analysis": technical_result,
                "risk_assessment": risk_result,
                "anomaly_detection": anomaly_check,
                "final_decision": final_decision,
                "confidence_score": self._calculate_confidence(
                    sentiment_result, technical_result, risk_result
                ),
                "metadata": {
                    "technical_indicators": technical_indicators,
                    "news_count": len(news_data.get("articles", [])) if news_data else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error in multi-model analysis for {symbol}: {str(e)}")
            raise
    
    async def _fetch_news_async(self, symbol: str) -> Dict[str, Any]:
        """Fetch news data asynchronously."""
        try:
            return await asyncio.to_thread(self.news_service.get_company_news, symbol, days=7)
        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {str(e)}")
            return {"articles": [], "sentiment": {"overall": "neutral", "score": 0.5}}
    
    async def _fetch_technical_async(self, symbol: str, historical_data: Optional[Dict]) -> Dict[str, Any]:
        """Fetch technical indicators asynchronously."""
        try:
            if historical_data:
                return await asyncio.to_thread(
                    self.technical_service.calculate_indicators,
                    historical_data
                )
            return {}
        except Exception as e:
            logger.error(f"Error calculating technical indicators for {symbol}: {str(e)}")
            return {}
    
    async def _analyze_sentiment(self, symbol: str, news_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sentiment Analysis using fast Llama 70B model.
        Optimized for quick news sentiment processing.
        """
        try:
            articles = news_data.get("articles", [])[:5]  # Top 5 news
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a financial news sentiment analyzer.
Analyze the news and provide:
1. Overall sentiment (bullish/bearish/neutral)
2. Sentiment score (0-100)
3. Key sentiment drivers
4. Market mood

Be concise and factual."""),
                ("human", f"""Stock: {symbol}

Recent News:
{self._format_news(articles)}

Provide sentiment analysis in this format:
SENTIMENT: [bullish/bearish/neutral]
SCORE: [0-100]
DRIVERS: [key points]
MOOD: [market sentiment]""")
            ])
            
            chain = prompt | self.sentiment_model
            response = await asyncio.to_thread(chain.invoke, {})
            
            return self._parse_sentiment_response(response.content)
            
        except Exception as e:
            logger.error(f"Sentiment analysis error: {str(e)}")
            return {"sentiment": "neutral", "score": 50, "error": str(e)}
    
    async def _analyze_technical(
        self,
        symbol: str,
        current_price: float,
        technical_indicators: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Technical Analysis using Mistral 8x7B model.
        Specialized for pattern recognition and technical interpretation.
        """
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a technical analysis expert.
Interpret technical indicators and identify patterns.
Provide:
1. Signal (buy/sell/hold)
2. Strength (0-100)
3. Key indicators
4. Pattern recognition

Focus on RSI, SMA, volume, and momentum."""),
                ("human", f"""Stock: {symbol}
Current Price: ₹{current_price}

Technical Indicators:
{self._format_technical_indicators(technical_indicators)}

Provide technical analysis in this format:
SIGNAL: [buy/sell/hold]
STRENGTH: [0-100]
KEY_INDICATORS: [important signals]
PATTERNS: [identified patterns]""")
            ])
            
            chain = prompt | self.technical_model
            response = await asyncio.to_thread(chain.invoke, {})
            
            return self._parse_technical_response(response.content)
            
        except Exception as e:
            logger.error(f"Technical analysis error: {str(e)}")
            return {"signal": "hold", "strength": 50, "error": str(e)}
    
    async def _assess_risk(
        self,
        symbol: str,
        current_price: float,
        technical_indicators: Dict[str, Any],
        news_data: Dict[str, Any],
        price_change_percent: Optional[float]
    ) -> Dict[str, Any]:
        """
        Risk Assessment using advanced Llama 405B model.
        Deep analysis of risk factors and scenario planning.
        """
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a risk assessment expert for stock trading.
Perform deep risk analysis considering:
1. Market volatility
2. News impact
3. Technical risks
4. Downside scenarios
5. Risk-reward ratio

Provide comprehensive risk evaluation."""),
                ("human", f"""Stock: {symbol}
Current Price: ₹{current_price}
Price Change: {price_change_percent}%

Risk Analysis Request:
- Evaluate downside risk
- Identify risk factors
- Calculate risk-reward ratio
- Provide risk score (0-100, where 100 is highest risk)

Provide risk assessment in this format:
RISK_SCORE: [0-100]
RISK_LEVEL: [low/medium/high/extreme]
RISK_FACTORS: [key risks]
DOWNSIDE: [potential loss scenarios]
RISK_REWARD: [ratio]""")
            ])
            
            chain = prompt | self.risk_model
            response = await asyncio.to_thread(chain.invoke, {})
            
            return self._parse_risk_response(response.content)
            
        except Exception as e:
            logger.error(f"Risk assessment error: {str(e)}")
            return {"risk_score": 50, "risk_level": "medium", "error": str(e)}
    
    async def _detect_anomaly(
        self,
        symbol: str,
        current_price: float,
        price_change_percent: Optional[float],
        technical_indicators: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Anomaly Detection using fast Llama 70B model.
        Identifies unusual market behavior for alerts.
        """
        try:
            if price_change_percent is None:
                return {"anomaly_detected": False, "reason": "No price change data"}
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an anomaly detection system for stock markets.
Detect unusual patterns:
1. Unusual price movements
2. Volume spikes
3. Technical divergences
4. Flash crashes/spikes

Be precise and alert-focused."""),
                ("human", f"""Stock: {symbol}
Current Price: ₹{current_price}
Price Change: {price_change_percent}%
RSI: {technical_indicators.get('rsi', 'N/A')}
Volume: {technical_indicators.get('volume', 'N/A')}

Detect anomalies in this format:
ANOMALY: [yes/no]
TYPE: [spike/crash/divergence/volume_surge/none]
SEVERITY: [low/medium/high]
REASON: [explanation]""")
            ])
            
            chain = prompt | self.anomaly_model
            response = await asyncio.to_thread(chain.invoke, {})
            
            return self._parse_anomaly_response(response.content)
            
        except Exception as e:
            logger.error(f"Anomaly detection error: {str(e)}")
            return {"anomaly_detected": False, "error": str(e)}
    
    async def _generate_ensemble_decision(
        self,
        symbol: str,
        current_price: float,
        sentiment: Dict[str, Any],
        technical: Dict[str, Any],
        risk: Dict[str, Any],
        price_change_percent: Optional[float]
    ) -> Dict[str, Any]:
        """
        Generate final trading decision by combining all model outputs.
        Uses weighted ensemble approach.
        """
        try:
            # Weighted scoring
            sentiment_score = sentiment.get("score", 50)
            technical_strength = technical.get("strength", 50)
            risk_score = 100 - risk.get("risk_score", 50)  # Invert risk (lower risk = higher score)
            
            # Ensemble score (weighted average)
            ensemble_score = (
                sentiment_score * 0.3 +
                technical_strength * 0.4 +
                risk_score * 0.3
            )
            
            # Determine action
            if ensemble_score >= 70:
                action = "BUY"
                confidence = "HIGH"
            elif ensemble_score >= 55:
                action = "BUY"
                confidence = "MEDIUM"
            elif ensemble_score >= 45:
                action = "HOLD"
                confidence = "MEDIUM"
            elif ensemble_score >= 30:
                action = "SELL"
                confidence = "MEDIUM"
            else:
                action = "SELL"
                confidence = "HIGH"
            
            # Generate reasoning
            reasoning = self._generate_reasoning(sentiment, technical, risk, action)
            
            return {
                "action": action,
                "confidence": confidence,
                "ensemble_score": round(ensemble_score, 2),
                "reasoning": reasoning,
                "model_votes": {
                    "sentiment": sentiment.get("sentiment", "neutral"),
                    "technical": technical.get("signal", "hold"),
                    "risk": risk.get("risk_level", "medium")
                },
                "target_price": self._calculate_target_price(current_price, action, ensemble_score),
                "stop_loss": self._calculate_stop_loss(current_price, action, risk.get("risk_score", 50))
            }
            
        except Exception as e:
            logger.error(f"Ensemble decision error: {str(e)}")
            return {
                "action": "HOLD",
                "confidence": "LOW",
                "ensemble_score": 50,
                "reasoning": "Error in ensemble analysis",
                "error": str(e)
            }
    
    def _handle_result(self, result: Any, default_message: str) -> Dict[str, Any]:
        """Handle result or exception from async tasks."""
        if isinstance(result, Exception):
            logger.error(f"Task failed: {str(result)}")
            return {"error": str(result), "message": default_message}
        return result
    
    def _calculate_confidence(
        self,
        sentiment: Dict[str, Any],
        technical: Dict[str, Any],
        risk: Dict[str, Any]
    ) -> float:
        """Calculate overall confidence score based on model agreement."""
        scores = []
        
        if "score" in sentiment:
            scores.append(sentiment["score"])
        if "strength" in technical:
            scores.append(technical["strength"])
        if "risk_score" in risk:
            scores.append(100 - risk["risk_score"])
        
        if not scores:
            return 50.0
        
        # Calculate variance (agreement metric)
        avg = sum(scores) / len(scores)
        variance = sum((x - avg) ** 2 for x in scores) / len(scores)
        
        # Higher variance = lower confidence
        confidence = max(0, 100 - variance)
        return round(confidence, 2)
    
    def _format_news(self, articles: List[Dict]) -> str:
        """Format news articles for prompt."""
        if not articles:
            return "No recent news available."
        
        formatted = []
        for i, article in enumerate(articles[:5], 1):
            formatted.append(f"{i}. {article.get('title', 'No title')}")
        return "\n".join(formatted)
    
    def _format_technical_indicators(self, indicators: Dict[str, Any]) -> str:
        """Format technical indicators for prompt."""
        if not indicators:
            return "No technical indicators available."
        
        formatted = []
        for key, value in indicators.items():
            if isinstance(value, (int, float)):
                formatted.append(f"{key.upper()}: {value:.2f}")
            else:
                formatted.append(f"{key.upper()}: {value}")
        return "\n".join(formatted)
    
    def _parse_sentiment_response(self, response: str) -> Dict[str, Any]:
        """Parse sentiment model response."""
        try:
            lines = response.strip().split("\n")
            result = {}
            
            for line in lines:
                if "SENTIMENT:" in line:
                    result["sentiment"] = line.split(":", 1)[1].strip().lower()
                elif "SCORE:" in line:
                    result["score"] = float(line.split(":", 1)[1].strip())
                elif "DRIVERS:" in line:
                    result["drivers"] = line.split(":", 1)[1].strip()
                elif "MOOD:" in line:
                    result["mood"] = line.split(":", 1)[1].strip()
            
            return result
        except Exception as e:
            logger.error(f"Error parsing sentiment response: {str(e)}")
            return {"sentiment": "neutral", "score": 50, "raw": response}
    
    def _parse_technical_response(self, response: str) -> Dict[str, Any]:
        """Parse technical model response."""
        try:
            lines = response.strip().split("\n")
            result = {}
            
            for line in lines:
                if "SIGNAL:" in line:
                    result["signal"] = line.split(":", 1)[1].strip().lower()
                elif "STRENGTH:" in line:
                    result["strength"] = float(line.split(":", 1)[1].strip())
                elif "KEY_INDICATORS:" in line:
                    result["key_indicators"] = line.split(":", 1)[1].strip()
                elif "PATTERNS:" in line:
                    result["patterns"] = line.split(":", 1)[1].strip()
            
            return result
        except Exception as e:
            logger.error(f"Error parsing technical response: {str(e)}")
            return {"signal": "hold", "strength": 50, "raw": response}
    
    def _parse_risk_response(self, response: str) -> Dict[str, Any]:
        """Parse risk model response."""
        try:
            lines = response.strip().split("\n")
            result = {}
            
            for line in lines:
                if "RISK_SCORE:" in line:
                    result["risk_score"] = float(line.split(":", 1)[1].strip())
                elif "RISK_LEVEL:" in line:
                    result["risk_level"] = line.split(":", 1)[1].strip().lower()
                elif "RISK_FACTORS:" in line:
                    result["risk_factors"] = line.split(":", 1)[1].strip()
                elif "DOWNSIDE:" in line:
                    result["downside"] = line.split(":", 1)[1].strip()
                elif "RISK_REWARD:" in line:
                    result["risk_reward"] = line.split(":", 1)[1].strip()
            
            return result
        except Exception as e:
            logger.error(f"Error parsing risk response: {str(e)}")
            return {"risk_score": 50, "risk_level": "medium", "raw": response}
    
    def _parse_anomaly_response(self, response: str) -> Dict[str, Any]:
        """Parse anomaly detection response."""
        try:
            lines = response.strip().split("\n")
            result = {}
            
            for line in lines:
                if "ANOMALY:" in line:
                    result["anomaly_detected"] = "yes" in line.lower()
                elif "TYPE:" in line:
                    result["type"] = line.split(":", 1)[1].strip()
                elif "SEVERITY:" in line:
                    result["severity"] = line.split(":", 1)[1].strip()
                elif "REASON:" in line:
                    result["reason"] = line.split(":", 1)[1].strip()
            
            return result
        except Exception as e:
            logger.error(f"Error parsing anomaly response: {str(e)}")
            return {"anomaly_detected": False, "raw": response}
    
    def _generate_reasoning(
        self,
        sentiment: Dict[str, Any],
        technical: Dict[str, Any],
        risk: Dict[str, Any],
        action: str
    ) -> str:
        """Generate human-readable reasoning for the decision."""
        reasons = []
        
        # Sentiment reasoning
        sent = sentiment.get("sentiment", "neutral")
        if sent == "bullish":
            reasons.append("Positive market sentiment from news")
        elif sent == "bearish":
            reasons.append("Negative market sentiment from news")
        
        # Technical reasoning
        signal = technical.get("signal", "hold")
        if signal == "buy":
            reasons.append("Technical indicators show buying opportunity")
        elif signal == "sell":
            reasons.append("Technical indicators suggest selling")
        
        # Risk reasoning
        risk_level = risk.get("risk_level", "medium")
        if risk_level == "high" or risk_level == "extreme":
            reasons.append(f"High risk detected: {risk.get('risk_factors', 'multiple factors')}")
        elif risk_level == "low":
            reasons.append("Low risk environment supports position")
        
        return " | ".join(reasons) if reasons else f"Consolidated analysis suggests {action}"
    
    def _calculate_target_price(self, current_price: float, action: str, score: float) -> float:
        """Calculate target price based on action and confidence."""
        if action == "BUY":
            # Target 3-8% gain based on score
            gain_percent = 3 + (score - 50) * 0.1
            return round(current_price * (1 + gain_percent / 100), 2)
        elif action == "SELL":
            # Exit with minimal loss
            return round(current_price * 0.98, 2)
        else:
            return current_price
    
    def _calculate_stop_loss(self, current_price: float, action: str, risk_score: float) -> float:
        """Calculate stop loss based on risk."""
        if action == "BUY":
            # Stop loss 2-5% based on risk
            loss_percent = 2 + (risk_score / 100) * 3
            return round(current_price * (1 - loss_percent / 100), 2)
        elif action == "SELL":
            # Stop loss if price goes up
            return round(current_price * 1.02, 2)
        else:
            return round(current_price * 0.97, 2)


# Global orchestrator instance
orchestrator = MultiModelOrchestrator()
