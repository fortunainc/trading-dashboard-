"""
Data Service Layer
Integrated data fetching with caching, validation, and fallback chains
"""

from typing import Optional, Dict, List, Any
import logging

from app.config import Settings
from app.failure_handler import FailureHandler
from app.data_sources.tradier_client import TradierClient
from app.data_sources.yahoo_client import YahooFinanceClient
from app.data_sources.alpha_vantage_client import AlphaVantageClient
from app.data_sources.finnhub_client import FinnhubClient
from app.data_sources.data_normalizer import DataNormalizer, NormalizedDataResult
from app.data_sources.data_validator import DataValidator, ValidationResult
from app.data_sources.cache_manager import CacheManager
from app.models.price_data import TickerPriceData
from app.models.ohlcv import OHLCVSeries

logger = logging.getLogger(__name__)


class DataService:
    """
    High-level data service combining all data sources,
    caching, validation, and failure handling
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
        
        # Initialize failure handler
        self.failure_handler = FailureHandler(
            failure_threshold=3,
            cooldown_seconds=300
        )
        
        # Initialize cache manager
        self.cache_manager = CacheManager(settings.REDIS_URL)
        
        # Initialize data source clients
        self.tradier = TradierClient(settings.TRADIER_API_KEY) if settings.TRADIER_API_KEY else None
        self.yahoo = YahooFinanceClient()
        self.alpha_vantage = AlphaVantageClient(settings.ALPHA_VANTAGE_API_KEY) if settings.ALPHA_VANTAGE_API_KEY else None
        self.finnhub = FinnhubClient(settings.FINNHUB_API_KEY) if settings.FINNHUB_API_KEY else None
        
        # Initialize normalizer
        self.normalizer = DataNormalizer(
            tradier_client=self.tradier,
            yahoo_client=self.yahoo,
            alpha_vantage_client=self.alpha_vantage,
            finnhub_client=self.finnhub
        )
        
        # Initialize validator
        self.validator = DataValidator(enable_strict_mode=settings.STRICT_VALIDATION)
    
    async def initialize(self):
        """Initialize data service connections"""
        try:
            await self.cache_manager.initialize()
            logger.info("Data service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize data service: {str(e)}")
            raise
    
    async def close(self):
        """Close data service connections"""
        try:
            await self.cache_manager.close()
            logger.info("Data service closed successfully")
        except Exception as e:
            logger.error(f"Error closing data service: {str(e)}")
    
    async def get_price_data(
        self,
        symbol: str,
        include_after_hours: bool = True,
        include_premarket: bool = True,
        include_live: bool = False,
        use_cache: bool = True,
        force_refresh: bool = False
    ) -> tuple[Optional[TickerPriceData], ValidationResult]:
        """
        Get price data with caching, validation, and fallback
        
        Args:
            symbol: Stock symbol
            include_after_hours: Include after-hours data
            include_premarket: Include premarket data
            include_live: Include live data
            use_cache: Use cached data if available
            force_refresh: Force fetch from API ignoring cache
        
        Returns:
            Tuple of (price_data or None, validation_result)
        """
        # Check cache first
        cached_data = None
        if use_cache and not force_refresh:
            cached_data = await self.cache_manager.get_price_data(
                symbol, include_after_hours, include_premarket, include_live
            )
            
            if cached_data:
                logger.info(f"Using cached price data for {symbol}")
                # Convert dict back to TickerPriceData
                from app.models.price_data import TickerPriceData
                price_data = TickerPriceData(**cached_data)
                validation = self.validator.validate_price_data(price_data)
                return price_data, validation
        
        # Fetch fresh data with failure handling
        result = await self.failure_handler.safe_execute(
            func=self.normalizer.get_normalized_price_data,
            service_name="price_data",
            fallback_value=None,
            symbol=symbol,
            include_after_hours=include_after_hours,
            include_premarket=include_premarket,
            include_live=include_live
        )
        
        if not result.success:
            logger.error(f"Failed to get price data for {symbol}: {result.error}")
            # Return cached data if available
            if cached_data:
                logger.warning(f"Using stale cached data for {symbol}")
                from app.models.price_data import TickerPriceData
                price_data = TickerPriceData(**cached_data)
                validation = self.validator.validate_price_data(price_data)
                return price_data, validation
            return None, ValidationResult(is_valid=False, errors=[result.error])
        
        # Validate data
        price_data = result.data
        validation = self.validator.validate_price_data(price_data)
        
        if not validation.is_valid:
            logger.error(f"Price data validation failed for {symbol}: {validation.errors}")
        
        # Cache valid data
        if validation.is_valid or self.settings.CACHE_VALIDATED_ONLY:
            await self.cache_manager.set_price_data(
                symbol,
                price_data.__dict__,
                include_after_hours,
                include_premarket,
                include_live
            )
        
        return price_data, validation
    
    async def get_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1d",
        limit: int = 100,
        use_cache: bool = True,
        force_refresh: bool = False
    ) -> tuple[Optional[OHLCVSeries], ValidationResult]:
        """
        Get OHLCV data with caching, validation, and fallback
        
        Args:
            symbol: Stock symbol
            timeframe: Timeframe (1d, 15m, 1h)
            limit: Number of candles
            use_cache: Use cached data if available
            force_refresh: Force fetch from API ignoring cache
        
        Returns:
            Tuple of (ohlcv or None, validation_result)
        """
        # Check cache first
        cached_data = None
        if use_cache and not force_refresh:
            cached_data = await self.cache_manager.get_ohlcv(symbol, timeframe, limit)
            
            if cached_data:
                logger.info(f"Using cached OHLCV for {symbol} {timeframe}")
                ohlcv = OHLCVSeries(**cached_data)
                validation = self.validator.validate_ohlcv(ohlcv)
                return ohlcv, validation
        
        # Fetch fresh data with failure handling
        result = await self.failure_handler.safe_execute(
            func=self.normalizer.get_normalized_ohlcv,
            service_name="ohlcv",
            fallback_value=None,
            symbol=symbol,
            timeframe=timeframe,
            limit=limit
        )
        
        if not result.success:
            logger.error(f"Failed to get OHLCV for {symbol}: {result.error}")
            # Return cached data if available
            if cached_data:
                logger.warning(f"Using stale cached OHLCV for {symbol}")
                ohlcv = OHLCVSeries(**cached_data)
                validation = self.validator.validate_ohlcv(ohlcv)
                return ohlcv, validation
            return None, ValidationResult(is_valid=False, errors=[result.error])
        
        # Validate data
        ohlcv = result.data
        validation = self.validator.validate_ohlcv(ohlcv)
        
        if not validation.is_valid:
            logger.warning(f"OHLCV validation warnings for {symbol}: {validation.warnings}")
        
        # Cache valid data
        if validation.is_valid or self.settings.CACHE_VALIDATED_ONLY:
            await self.cache_manager.set_ohlcv(
                symbol,
                timeframe,
                [candle.__dict__ for candle in ohlcv.candles],
                limit
            )
        
        return ohlcv, validation
    
    async def get_catalyst_data(
        self,
        symbol: str,
        days_back: int = 7,
        use_cache: bool = True,
        force_refresh: bool = False
    ) -> Optional[Dict]:
        """
        Get catalyst data (news, earnings, events)
        
        Args:
            symbol: Stock symbol
            days_back: Number of days to look back
            use_cache: Use cached data if available
            force_refresh: Force fetch from API ignoring cache
        
        Returns:
            Catalyst data or None
        """
        # Check cache first
        if use_cache and not force_refresh:
            cached_data = await self.cache_manager.get_catalyst_data(symbol, days_back)
            if cached_data:
                logger.info(f"Using cached catalyst data for {symbol}")
                return cached_data
        
        # Fetch fresh data
        result = await self.failure_handler.safe_execute(
            func=self.normalizer.get_catalyst_data,
            service_name="catalyst",
            fallback_value=None,
            symbol=symbol,
            days_back=days_back
        )
        
        if result.success:
            catalyst_data = result.data
            # Cache result
            await self.cache_manager.set_catalyst_data(symbol, catalyst_data, days_back)
            return catalyst_data
        
        logger.error(f"Failed to get catalyst data for {symbol}: {result.error}")
        return None
    
    async def invalidate_cache(self, symbol: str):
        """
        Invalidate all cached data for a symbol
        
        Args:
            symbol: Stock symbol
        """
        logger.info(f"Invalidating cache for {symbol}")
        await self.cache_manager.invalidate_symbol(symbol)
    
    def is_connected(self) -> bool:
        """
        Check if data service is connected to required services
        
        Returns:
            True if connected, False otherwise
        """
        return self.cache_manager.is_connected()
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache stats
        """
        return await self.cache_manager.get_cache_stats()
    
    async def batch_get_price_data(
        self,
        symbols: List[str],
        include_after_hours: bool = True,
        include_premarket: bool = True,
        include_live: bool = False
    ) -> Dict[str, tuple[Optional[TickerPriceData], ValidationResult]]:
        """
        Get price data for multiple symbols
        
        Args:
            symbols: List of stock symbols
            include_after_hours: Include after-hours data
            include_premarket: Include premarket data
            include_live: Include live data
        
        Returns:
            Dictionary mapping symbol to (price_data, validation_result)
        """
        results = {}
        
        for symbol in symbols:
            price_data, validation = await self.get_price_data(
                symbol,
                include_after_hours,
                include_premarket,
                include_live
            )
            results[symbol] = (price_data, validation)
        
        return results
    
    def get_failure_status(self) -> Dict[str, Any]:
        """
        Get status of all service failures
        
        Returns:
            Dictionary with failure status
        """
        return self.failure_handler.get_all_status()