"""
Configuration module for the Agentic Stock Analysis Platform.
Loads environment variables and provides centralized configuration.
"""
import os
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    
    # MarketAux API
    MARKETAUX_API_KEY: str = os.getenv("MARKETAUX_API_KEY", "")
    
    # NVIDIA API Configuration (build.nvidia.com)
    NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY", "")
    NVIDIA_BASE_URL: str = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
    NVIDIA_MODEL: str = os.getenv("NVIDIA_MODEL", "meta/llama-3.1-405b-instruct")
    
    # Firebase
    FIREBASE_SERVICE_ACCOUNT_PATH: str = os.getenv(
        "FIREBASE_SERVICE_ACCOUNT_PATH", 
        "./serviceAccountKey.json"
    )
    
    # FastAPI Configuration
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Stock Monitoring Configuration
    WATCHLIST_SYMBOLS: str = os.getenv(
        "WATCHLIST_SYMBOLS", 
        "TATAMOTORS,RELIANCE,TCS,INFY"
    )
    PRICE_DROP_THRESHOLD: float = float(os.getenv("PRICE_DROP_THRESHOLD", "2.0"))
    PRICE_SPIKE_THRESHOLD: float = float(os.getenv("PRICE_SPIKE_THRESHOLD", "2.0"))
    
    @property
    def watchlist_symbols_list(self) -> List[str]:
        """Returns watchlist symbols as a list."""
        return [s.strip() for s in self.WATCHLIST_SYMBOLS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
