"""
Configuration and environment variables
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "trading-dashboard"
    app_env: str = "development"
    app_version: str = "1.0.0"
    debug: bool = True
    log_level: str = "INFO"
    
    # API Keys
    tradier_api_key: str = ""
    tradier_api_url: str = "https://api.tradier.com/v1"
    yahoo_api_url: str = "https://query1.finance.yahoo.com/v8/finance/chart"
    alpha_vantage_api_key: str = ""
    alpha_vantage_api_url: str = "https://www.alphavantage.co/query"
    finnhub_api_key: str = ""
    finnhub_api_url: str = "https://finnhub.io/api/v1"
    
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/trading_dashboard"
    database_pool_size: int = 20
    database_max_overflow: int = 10
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_ttl: int = 300  # 5 minutes
    redis_max_connections: int = 50
    
    # Data Validation
    strict_validation: bool = True
    cache_validated_only: bool = False
    
    # Analysis Configuration
    watchlist: str = "NVDA,META,TSLA,AAPL,GOOGL,AMZN,MSFT"
    max_scalp_setups: int = 4
    max_swing_setups: int = 3
    min_scalp_score: int = 60
    min_swing_score: int = 60
    
    # Time Configuration
    timezone: str = "America/New_York"
    market_open_time: str = "09:30:00"
    market_close_time: str = "16:00:00"
    premarket_start_time: str = "04:00:00"
    after_hours_end_time: str = "20:00:00"
    
    # WebSocket
    ws_port: int = 8001
    ws_reconnect_interval: int = 5000
    
    # Circuit Breaker
    circuit_breaker_failure_threshold: int = 3
    circuit_breaker_cooldown_seconds: int = 300
    
    # External Service Timeouts
    tradier_timeout: int = 10
    yahoo_timeout: int = 10
    alpha_vantage_timeout: int = 10
    finnhub_timeout: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def get_watchlist_list(self) -> List[str]:
        """Parse watchlist string into list"""
        return [s.strip() for s in self.watchlist.split(",") if s.strip()]


settings = Settings()