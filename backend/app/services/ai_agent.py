"""
AI Agent Service using LangChain + NVIDIA build.nvidia API.
Orchestrates news analysis, technical indicators, and generates actionable insights.
"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Dict, Any, Optional
from app.config import settings
from app.services.marketaux import MarketAuxService
from app.services.technical_analysis import TechnicalAnalysisService


class AIAgentService:
    """AI Agent for stock analysis and prediction."""
    
    def __init__(self):
        """Initialize LangChain with NVIDIA API."""
        self.llm = ChatOpenAI(
            model=settings.NVIDIA_MODEL,
            temperature=0.3,  # Lower temperature for more consistent analysis
            openai_api_key=settings.NVIDIA_API_KEY,
            openai_api_base=settings.NVIDIA_BASE_URL
        )
    
    async def analyze_stock(
        self,
        symbol: str,
        current_price: float,
        technical_indicators: Dict[str, Any],
        news_data: Dict[str, Any],
        price_change_percent: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive stock analysis using AI agent.
        
        Args:
            symbol: Stock symbol
            current_price: Current trading price
            technical_indicators: Technical analysis results
            news_data: News and sentiment data
            price_change_percent: Recent price change percentage (optional)
            
        Returns:
            AI-generated analysis with verdict and explanation
        """
        # Build context for the AI agent
        context = self._build_analysis_context(
            symbol=symbol,
            current_price=current_price,
            technical_indicators=technical_indicators,
            news_data=news_data,
            price_change_percent=price_change_percent
        )
        
        # Create the analysis prompt
        system_prompt = """You are an expert Indian stock market analyst with deep knowledge of NSE/BSE markets.
Your role is to analyze stocks based on:
1. Technical indicators (RSI, SMA, MACD, Bollinger Bands)
2. News sentiment analysis
3. Price movements and volume patterns

Provide clear, actionable insights with a BUY, SELL, or HOLD recommendation.
Always consider the Indian market context and regulatory environment."""

        user_prompt = f"""Analyze the following stock and provide your verdict:

STOCK: {symbol}
CURRENT PRICE: ₹{current_price}
{f'PRICE CHANGE: {price_change_percent:+.2f}%' if price_change_percent else ''}

TECHNICAL INDICATORS:
{self._format_technical_indicators(technical_indicators)}

NEWS SENTIMENT:
{self._format_news_sentiment(news_data)}

TOP NEWS HEADLINES:
{self._format_news_headlines(news_data)}

Provide your analysis in the following JSON format:
{{
    "verdict": "BUY" | "SELL" | "HOLD",
    "confidence": <0.0 to 1.0>,
    "explanation": "<2-3 sentence summary>",
    "key_factors": [<list of 3-5 key decision factors>],
    "risk_level": "LOW" | "MEDIUM" | "HIGH",
    "target_price": <suggested target price or null>,
    "stop_loss": <suggested stop loss or null>,
    "time_horizon": "INTRADAY" | "SHORT_TERM" | "MEDIUM_TERM" | "LONG_TERM"
}}"""

        try:
            # Invoke the LLM
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            # Parse the response
            import json
            analysis_result = json.loads(response.content)
            
            # Add metadata
            analysis_result['symbol'] = symbol
            analysis_result['current_price'] = current_price
            analysis_result['timestamp'] = news_data.get('timestamp')
            analysis_result['technical_indicators'] = technical_indicators
            analysis_result['news_sentiment'] = news_data.get('aggregate_sentiment')
            
            return analysis_result
            
        except json.JSONDecodeError:
            # Fallback if LLM doesn't return valid JSON
            return {
                "verdict": technical_indicators.get('overall_signal', 'HOLD'),
                "confidence": 0.5,
                "explanation": response.content if 'response' in locals() else "Analysis completed based on technical indicators.",
                "key_factors": ["Technical analysis"],
                "risk_level": "MEDIUM",
                "target_price": None,
                "stop_loss": None,
                "time_horizon": "SHORT_TERM",
                "ai_reasoning": response.content if 'response' in locals() else ""
            }
        except Exception as e:
            print(f"❌ AI Agent error: {e}")
            return {
                "verdict": "HOLD",
                "confidence": 0.0,
                "explanation": f"Error in AI analysis: {str(e)}",
                "error": str(e)
            }
    
    def _build_analysis_context(
        self,
        symbol: str,
        current_price: float,
        technical_indicators: Dict[str, Any],
        news_data: Dict[str, Any],
        price_change_percent: Optional[float]
    ) -> str:
        """Build comprehensive context string for AI analysis."""
        context_parts = [
            f"Symbol: {symbol}",
            f"Current Price: ₹{current_price}",
        ]
        
        if price_change_percent:
            context_parts.append(f"Price Change: {price_change_percent:+.2f}%")
        
        return "\n".join(context_parts)
    
    def _format_technical_indicators(self, indicators: Dict[str, Any]) -> str:
        """Format technical indicators for prompt."""
        lines = []
        
        # RSI
        rsi = indicators.get('rsi', {})
        lines.append(f"- RSI: {rsi.get('value', 'N/A')} ({rsi.get('signal', 'unknown')})")
        
        # SMA
        sma = indicators.get('sma', {})
        lines.append(f"- SMA(20): {sma.get('sma_20', 'N/A')}")
        lines.append(f"- SMA(50): {sma.get('sma_50', 'N/A')}")
        lines.append(f"- SMA Signal: {sma.get('signal', 'unknown')}")
        
        # MACD
        macd = indicators.get('macd', {})
        lines.append(f"- MACD: {macd.get('macd', 'N/A')} ({macd.get('signal', 'unknown')})")
        
        # Bollinger Bands
        bb = indicators.get('bollinger_bands', {})
        lines.append(f"- Bollinger Bands: {bb.get('signal', 'unknown')}")
        
        # Overall
        lines.append(f"- Overall Technical Signal: {indicators.get('overall_signal', 'HOLD')}")
        
        return "\n".join(lines)
    
    def _format_news_sentiment(self, news_data: Dict[str, Any]) -> str:
        """Format news sentiment for prompt."""
        sentiment = news_data.get('aggregate_sentiment', {})
        
        lines = [
            f"- Overall Sentiment: {sentiment.get('overall', 'neutral').upper()}",
            f"- Average Polarity: {sentiment.get('average_polarity', 0.0)}",
            f"- Positive Articles: {sentiment.get('positive_count', 0)}",
            f"- Negative Articles: {sentiment.get('negative_count', 0)}",
            f"- Neutral Articles: {sentiment.get('neutral_count', 0)}",
            f"- Confidence: {sentiment.get('confidence', 0.0):.2f}",
        ]
        
        return "\n".join(lines)
    
    def _format_news_headlines(self, news_data: Dict[str, Any]) -> str:
        """Format top news headlines for prompt."""
        articles = news_data.get('data', [])[:5]  # Top 5 articles
        
        if not articles:
            return "No recent news available."
        
        lines = []
        for i, article in enumerate(articles, 1):
            title = article.get('title', 'N/A')
            sentiment = article.get('sentiment', {}).get('score', 'neutral')
            lines.append(f"{i}. [{sentiment.upper()}] {title}")
        
        return "\n".join(lines)


# Global AI Agent instance
ai_agent = AIAgentService()
