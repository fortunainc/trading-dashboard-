"""
Redis Cache Manager
Handles caching of price data, OHLCV, and analysis results
"""

import json
import hashlib
from typing import Optional, Any, Dict, List
from datetime import datetime, timedelta
import logging

import redis
from redis.asyncio import Redis as AsyncRedis

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages Redis caching for trading data"""
    
    # Cache TTL (time to live) in seconds
    TTL_PRICE_DATA = 300  # 5 minutes for live prices
    TTL_OFFICIAL_CLOSE = 3600  # 1 hour - official close doesn't change
    TTL_AFTER_HOURS = 180  # 3 minutes - needs to be fresh
    TTL_PREMARKET = 180  # 3 minutes - needs to be fresh
    TTL_OHLCV_DAILY = 1800  # 30 minutes - daily data
    TTL_OHLCV_INTRADAY = 60  # 1 minute - intraday data
    TTL_ANALYSIS = 300  # 5 minutes - analysis results
    TTL_CATALYST = 1800  # 30 minutes - news/events
    TTL_QUOTES = 60  # 1 minute - live quotes
    
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis_client: Optional[AsyncRedis] = None
        self._connected = False
    
    async def initialize(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = AsyncRedis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            # Test connection
            await self.redis_client.ping()
            self._connected = True
            logger.info("Redis cache manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Redis connection: {str(e)}")
            self._connected = False
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            self._connected = False
            logger.info("Redis connection closed")
    
    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        return self._connected
    
    async def get_price_data(
        self,
        symbol: str,
        include_after_hours: bool = True,
        include_premarket: bool = True,
        include_live: bool = False
    ) -> Optional[Dict]:
        """
        Get cached price data
        
        Args:
            symbol: Stock symbol
            include_after_hours: Include after-hours data
            include_premarket: Include premarket data
            include_live: Include live data
        
        Returns:
            Cached price data or None if not found/expired
        """
        if not self._connected:
            return None
        
        try:
            cache_key = self._generate_price_key(
                symbol, include_after_hours, include_premarket, include_live
            )
            
            cached = await self.redis_client.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for price data: {cache_key}")
                return json.loads(cached)
            
            logger.debug(f"Cache miss for price data: {cache_key}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting price data from cache: {str(e)}")
            return None
    
    async def set_price_data(
        self,
        symbol: str,
        price_data: Dict,
        include_after_hours: bool = True,
        include_premarket: bool = True,
        include_live: bool = False
    ) -> bool:
        """
        Cache price data
        
        Args:
            symbol: Stock symbol
            price_data: Price data to cache
            include_after_hours: Include after-hours data
            include_premarket: Include premarket data
            include_live: Include live data
        
        Returns:
            True if cached successfully, False otherwise
        """
        if not self._connected:
            return False
        
        try:
            cache_key = self._generate_price_key(
                symbol, include_after_hours, include_premarket, include_live
            )
            
            # Determine TTL based on data type
            if include_live:
                ttl = self.TTL_QUOTES
            elif include_after_hours or include_premarket:
                ttl = min(self.TTL_AFTER_HOURS, self.TTL_PREMARKET)
            else:
                ttl = self.TTL_OFFICIAL_CLOSE
            
            await self.redis_client.setex(
                cache_key,
                ttl,
                json.dumps(price_data, default=str)
            )
            
            logger.debug(f"Cached price data: {cache_key} (TTL: {ttl}s)")
            return True
            
        except Exception as e:
            logger.error(f"Error setting price data to cache: {str(e)}")
            return False
    
    async def get_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        limit: int
    ) -> Optional[List[Dict]]:
        """
        Get cached OHLCV data
        
        Args:
            symbol: Stock symbol
            timeframe: Timeframe (1d, 15m, 1h)
            limit: Number of candles
        
        Returns:
            Cached OHLCV data or None if not found/expired
        """
        if not self._connected:
            return None
        
        try:
            cache_key = self._generate_ohlcv_key(symbol, timeframe, limit)
            
            cached = await self.redis_client.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for OHLCV: {cache_key}")
                return json.loads(cached)
            
            logger.debug(f"Cache miss for OHLCV: {cache_key}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting OHLCV from cache: {str(e)}")
            return None
    
    async def set_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        ohlcv: List[Dict],
        limit: int
    ) -> bool:
        """
        Cache OHLCV data
        
        Args:
            symbol: Stock symbol
            timeframe: Timeframe (1d, 15m, 1h)
            ohlcv: OHLCV data to cache
            limit: Number of candles
        
        Returns:
            True if cached successfully, False otherwise
        """
        if not self._connected:
            return False
        
        try:
            cache_key = self._generate_ohlcv_key(symbol, timeframe, limit)
            
            # Determine TTL based on timeframe
            if timeframe == "1d":
                ttl = self.TTL_OHLCV_DAILY
            else:
                ttl = self.TTL_OHLCV_INTRADAY
            
            await self.redis_client.setex(
                cache_key,
                ttl,
                json.dumps(ohlcv, default=str)
            )
            
            logger.debug(f"Cached OHLCV: {cache_key} (TTL: {ttl}s)")
            return True
            
        except Exception as e:
            logger.error(f"Error setting OHLCV to cache: {str(e)}")
            return False
    
    async def get_analysis_result(
        self,
        symbol: str,
        mode: str,
        date: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Get cached analysis result
        
        Args:
            symbol: Stock symbol
            mode: Analysis mode (prep, live)
            date: Date string (for prep mode)
        
        Returns:
            Cached analysis or None if not found/expired
        """
        if not self._connected:
            return None
        
        try:
            cache_key = self._generate_analysis_key(symbol, mode, date)
            
            cached = await self.redis_client.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for analysis: {cache_key}")
                return json.loads(cached)
            
            logger.debug(f"Cache miss for analysis: {cache_key}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting analysis from cache: {str(e)}")
            return None
    
    async def set_analysis_result(
        self,
        symbol: str,
        mode: str,
        analysis: Dict,
        date: Optional[str] = None
    ) -> bool:
        """
        Cache analysis result
        
        Args:
            symbol: Stock symbol
            mode: Analysis mode (prep, live)
            analysis: Analysis result to cache
            date: Date string (for prep mode)
        
        Returns:
            True if cached successfully, False otherwise
        """
        if not self._connected:
            return False
        
        try:
            cache_key = self._generate_analysis_key(symbol, mode, date)
            
            await self.redis_client.setex(
                cache_key,
                self.TTL_ANALYSIS,
                json.dumps(analysis, default=str)
            )
            
            logger.debug(f"Cached analysis: {cache_key} (TTL: {self.TTL_ANALYSIS}s)")
            return True
            
        except Exception as e:
            logger.error(f"Error setting analysis to cache: {str(e)}")
            return False
    
    async def get_catalyst_data(
        self,
        symbol: str,
        days_back: int = 7
    ) -> Optional[Dict]:
        """
        Get cached catalyst data
        
        Args:
            symbol: Stock symbol
            days_back: Number of days to look back
        
        Returns:
            Cached catalyst data or None if not found/expired
        """
        if not self._connected:
            return None
        
        try:
            cache_key = f"catalyst:{symbol}:{days_back}"
            
            cached = await self.redis_client.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for catalyst: {cache_key}")
                return json.loads(cached)
            
            logger.debug(f"Cache miss for catalyst: {cache_key}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting catalyst from cache: {str(e)}")
            return None
    
    async def set_catalyst_data(
        self,
        symbol: str,
        catalyst_data: Dict,
        days_back: int = 7
    ) -> bool:
        """
        Cache catalyst data
        
        Args:
            symbol: Stock symbol
            catalyst_data: Catalyst data to cache
            days_back: Number of days to look back
        
        Returns:
            True if cached successfully, False otherwise
        """
        if not self._connected:
            return False
        
        try:
            cache_key = f"catalyst:{symbol}:{days_back}"
            
            await self.redis_client.setex(
                cache_key,
                self.TTL_CATALYST,
                json.dumps(catalyst_data, default=str)
            )
            
            logger.debug(f"Cached catalyst: {cache_key} (TTL: {self.TTL_CATALYST}s)")
            return True
            
        except Exception as e:
            logger.error(f"Error setting catalyst to cache: {str(e)}")
            return False
    
    async def invalidate_symbol(self, symbol: str):
        """
        Invalidate all cached data for a symbol
        
        Args:
            symbol: Stock symbol
        """
        if not self._connected:
            return
        
        try:
            # Find all keys for this symbol
            pattern = f"*{symbol}*"
            keys = []
            async for key in self.redis_client.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                await self.redis_client.delete(*keys)
                logger.info(f"Invalidated {len(keys)} cache entries for {symbol}")
            
        except Exception as e:
            logger.error(f"Error invalidating cache for {symbol}: {str(e)}")
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache statistics
        """
        if not self._connected:
            return {"connected": False}
        
        try:
            info = await self.redis_client.info()
            
            return {
                "connected": True,
                "used_memory_human": info.get("used_memory_human"),
                "used_memory_peak_human": info.get("used_memory_peak_human"),
                "total_keys": info.get("db0", {}).get("keys", 0),
                "hit_rate": info.get("keyspace_hits", 0) / (info.get("keyspace_hits", 1) + info.get("keyspace_misses", 1))
            }
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {str(e)}")
            return {"connected": True, "error": str(e)}
    
    def _generate_price_key(
        self,
        symbol: str,
        include_after_hours: bool,
        include_premarket: bool,
        include_live: bool
    ) -> str:
        """Generate cache key for price data"""
        components = [symbol.upper()]
        if include_after_hours:
            components.append("ah")
        if include_premarket:
            components.append("pm")
        if include_live:
            components.append("live")
        
        key = ":".join(["price"] + components)
        return key
    
    def _generate_ohlcv_key(
        self,
        symbol: str,
        timeframe: str,
        limit: int
    ) -> str:
        """Generate cache key for OHLCV data"""
        return f"ohlcv:{symbol.upper()}:{timeframe}:{limit}"
    
    def _generate_analysis_key(
        self,
        symbol: str,
        mode: str,
        date: Optional[str] = None
    ) -> str:
        """Generate cache key for analysis result"""
        if date:
            return f"analysis:{symbol.upper()}:{mode}:{date}"
        return f"analysis:{symbol.upper()}:{mode}"
    
    def _generate_hash(self, data: Any) -> str:
        """Generate hash from data for cache key"""
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.md5(data_str.encode()).hexdigest()[:8]