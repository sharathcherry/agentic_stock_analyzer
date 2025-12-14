"""
MarketAux News API Integration.
Fetches Indian financial news with sentiment analysis for stock symbols.
"""
import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.config import settings


class MarketAuxService:
    """Service class for MarketAux News API."""
    
    BASE_URL = "https://api.marketaux.com/v1"
    
    @staticmethod
    async def fetch_indian_news(
        symbols: Optional[List[str]] = None,
        limit: int = 10,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Fetch latest Indian financial news from MarketAux.
        
        Args:
            symbols: List of stock symbols to filter (e.g., ['TATAMOTORS'])
            limit: Number of articles to fetch (max 100)
            language: Language code (default: 'en')
            
        Returns:
            Dictionary containing news articles and metadata
        """
        endpoint = f"{MarketAuxService.BASE_URL}/news/all"
        
        # Build query parameters
        params = {
            "api_token": settings.MARKETAUX_API_KEY,
            "countries": "in",  # Strictly Indian news
            "language": language,
            "limit": min(limit, 100),  # API limit is 100
            "sort": "published_on",  # Most recent first
        }
        
        # Add symbols filter if provided
        if symbols:
            # Convert symbols to comma-separated string
            params["symbols"] = ",".join(symbols)
        
        # Add filter for financial/business categories
        params["filter_entities"] = "true"
        params["industries"] = "Financial,Technology,Materials,Energy"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(endpoint, params=params)
                response.raise_for_status()
                data = response.json()
                
                # Process and enrich the response
                processed_data = MarketAuxService._process_news_data(data)
                return processed_data
                
        except httpx.HTTPStatusError as e:
            print(f"❌ MarketAux API error: {e.response.status_code} - {e.response.text}")
            return {"data": [], "error": str(e)}
        except Exception as e:
            print(f"❌ Error fetching MarketAux news: {e}")
            return {"data": [], "error": str(e)}
    
    @staticmethod
    def _process_news_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and enrich news data with sentiment scores.
        
        Args:
            raw_data: Raw API response from MarketAux
            
        Returns:
            Processed news data with sentiment analysis
        """
        articles = raw_data.get("data", [])
        processed_articles = []
        
        for article in articles:
            processed_article = {
                "title": article.get("title", ""),
                "description": article.get("description", ""),
                "url": article.get("url", ""),
                "published_at": article.get("published_at", ""),
                "source": article.get("source", ""),
                "sentiment": MarketAuxService._extract_sentiment(article),
                "entities": article.get("entities", []),
                "symbols": article.get("symbols", []),
            }
            processed_articles.append(processed_article)
        
        # Calculate aggregate sentiment
        aggregate_sentiment = MarketAuxService._calculate_aggregate_sentiment(
            processed_articles
        )
        
        return {
            "data": processed_articles,
            "total": len(processed_articles),
            "aggregate_sentiment": aggregate_sentiment,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def _extract_sentiment(article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract sentiment information from article.
        MarketAux provides sentiment scores in the API response.
        
        Args:
            article: Individual article data
            
        Returns:
            Sentiment information
        """
        sentiment_scores = article.get("sentiment_scores", {})
        
        return {
            "score": article.get("sentiment", "neutral"),  # positive, negative, neutral
            "polarity": sentiment_scores.get("polarity", 0.0),  # -1 to 1
            "subjectivity": sentiment_scores.get("subjectivity", 0.5),  # 0 to 1
        }
    
    @staticmethod
    def _calculate_aggregate_sentiment(articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate aggregate sentiment from multiple articles.
        
        Args:
            articles: List of processed articles
            
        Returns:
            Aggregate sentiment metrics
        """
        if not articles:
            return {
                "overall": "neutral",
                "average_polarity": 0.0,
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0
            }
        
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        total_polarity = 0.0
        
        for article in articles:
            sentiment = article.get("sentiment", {})
            score = sentiment.get("score", "neutral")
            polarity = sentiment.get("polarity", 0.0)
            
            if score == "positive":
                positive_count += 1
            elif score == "negative":
                negative_count += 1
            else:
                neutral_count += 1
            
            total_polarity += polarity
        
        average_polarity = total_polarity / len(articles)
        
        # Determine overall sentiment
        if average_polarity > 0.2:
            overall = "positive"
        elif average_polarity < -0.2:
            overall = "negative"
        else:
            overall = "neutral"
        
        return {
            "overall": overall,
            "average_polarity": round(average_polarity, 3),
            "positive_count": positive_count,
            "negative_count": negative_count,
            "neutral_count": neutral_count,
            "confidence": min(abs(average_polarity) * 2, 1.0)  # 0 to 1
        }


# Example usage function
async def get_stock_news(symbol: str) -> Dict[str, Any]:
    """
    Convenience function to fetch news for a specific stock symbol.
    
    Args:
        symbol: Stock symbol (e.g., 'TATAMOTORS')
        
    Returns:
        News data with sentiment analysis
    """
    return await MarketAuxService.fetch_indian_news(symbols=[symbol], limit=10)
