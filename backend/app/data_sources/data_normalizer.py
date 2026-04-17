"""
Data Normalization Layer
Normalizes data from multiple sources into unified format
"""

from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import logging

from app.models.price_data import (
    TickerPriceData,
    OfficialClose,
    AfterHoursData,
    PremarketData,
    LiveData,
    OpeningRange,
    VWAP,
    SessionType
)
from app.models.ohlcv import OHLCVCandle, OHLCVSeries

from app.data_sources.tradier_client import TradierClient
from app.data_sources.yahoo_client import YahooClient
from app.data_sources.alpha_vantage_client import AlphaVantageClient
from app.data_sources.finnhub_client import FinnhubClient

logger = logging.getLogger(__name__)


@dataclass
class NormalizedDataResult:
    """Result of data normalization"""
    success: bool
    data: Optional[Any] = None
    source: Optional[str] = None
    error: Optional[str] = None
    warnings: List[str] = None


class DataNormalizer:
    """Normalizes and integrates data from multiple sources"""
    
    def __init__(
        self,
        tradier_client: Optional[TradierClient] = None,
        yahoo_client: Optional[YahooClient] = None,
        alpha_vantage_client: Optional[AlphaVantageClient] = None,
        finnhub_client: Optional[FinnhubClient] = None
    ):
        self.tradier = tradier_client
        self.yahoo = yahoo_client
        self.alpha_vantage = alpha_vantage_client
        self.finnhub = finnhub_client
        
        # Source priority for different data types
        self.price_source_priority = ["tradier", "yahoo", "alpha_vantage"]
        self.ohlcv_source_priority = ["yahoo", "alpha_vantage"]
        self.catalyst_source_priority = ["finnhub"]
        
    async def get_normalized_price_data(
        self,
        symbol: str,
        include_after_hours: bool = True,
        include_premarket: bool = True,
        include_live: bool = False
    ) -> NormalizedDataResult:
        """
        Get normalized price data from best available source
        
        Args:
            symbol: Stock symbol
            include_after_hours: Include after-hours data
            include_premarket: Include premarket data
            include_live: Include live/real-time data
        
        Returns:
            NormalizedDataResult with TickerPriceData
        """
        warnings = []
        
        # Try sources in priority order
        for source_name in self.price_source_priority:
            try:
                if source_name == "tradier" and self.tradier:
                    result = await self._get_price_from_tradier(
                        symbol, include_after_hours, include_premarket, include_live
                    )
                elif source_name == "yahoo" and self.yahoo:
                    result = await self._get_price_from_yahoo(
                        symbol, include_after_hours, include_premarket, include_live
                    )
                elif source_name == "alpha_vantage" and self.alpha_vantage:
                    result = await self._get_price_from_alpha_vantage(
                        symbol, include_after_hours, include_premarket, include_live
                    )
                else:
                    continue
                
                if result.success:
                    result.source = source_name
                    result.warnings = warnings
                    return result
                else:
                    warnings.append(f"{source_name}: {result.error}")
                    
            except Exception as e:
                logger.warning(f"{source_name} failed for {symbol}: {str(e)}")
                warnings.append(f"{source_name}: {str(e)}")
                continue
        
        return NormalizedDataResult(
            success=False,
            error=f"All sources failed for {symbol}",
            warnings=warnings
        )
    
    async def _get_price_from_tradier(
        self,
        symbol: str,
        include_after_hours: bool,
        include_premarket: bool,
        include_live: bool
    ) -> NormalizedDataResult:
        """Get price data from Tradier"""
        try:
            # Get official close from previous day
            quote = await self.tradier.get_quote(symbol)
            if not quote:
                return NormalizedDataResult(success=False, error="No quote data")
            
            # Parse quote data
            price = quote.get("last", 0)
            prev_close = quote.get("prevclose", 0)
            change = price - prev_close
            change_percent = (change / prev_close * 100) if prev_close > 0 else 0
            
            official_close = OfficialClose(
                price=prev_close,
                change=0,
                change_percent=0,
                timestamp=datetime.now() - timedelta(days=1),
                source="tradier"
            )
            
            # After-hours data (if available)
            after_hours = AfterHoursData(price=0, change=0, change_percent=0, source=None, timestamp=None)
            if include_after_hours and quote.get("lasttradedatetime"):
                # Tradier provides extended hours quote
                after_hours = AfterHoursData(
                    price=price,
                    change=change,
                    change_percent=change_percent,
                    source="tradier",
                    timestamp=quote.get("lasttradedatetime")
                )
            
            # Premarket data (if available)
            premarket = PremarketData(price=0, change=0, change_percent=0, source=None, timestamp=None)
            if include_premarket:
                # Tradier may provide premarket data in extended hours
                premarket = premarket  # Placeholder - would need extended hours API
            
            # Live data
            live = LiveData(
                price=price,
                change=change,
                change_percent=change_percent,
                bid=quote.get("bid", 0),
                ask=quote.get("ask", 0),
                bid_size=quote.get("bidsize", 0),
                ask_size=quote.get("asksize", 0),
                volume=quote.get("volume", 0),
                high=quote.get("high", 0),
                low=quote.get("low", 0),
                open=quote.get("open", 0),
                source="tradier",
                timestamp=quote.get("lasttradedatetime", datetime.now())
            ) if include_live else None
            
            # Calculate differences
            differences = {}
            if after_hours.price > 0:
                differences["after_hours_vs_close"] = after_hours.price - official_close.price
            
            data = TickerPriceData(
                symbol=symbol,
                official_close=official_close,
                after_hours=after_hours,
                premarket=premarket,
                live=live,
                opening_range=OpeningRange(high=0, low=0, calculated_at=None),
                vwap=VWAP(price=0, calculated_at=None),
                differences=differences,
                last_updated=datetime.now(),
                data_quality="high",
                session_type=SessionType.LIVE if include_live else SessionType.PRE_MARKET
            )
            
            return NormalizedDataResult(success=True, data=data)
            
        except Exception as e:
            logger.error(f"Tradier price data error: {str(e)}")
            return NormalizedDataResult(success=False, error=str(e))
    
    async def _get_price_from_yahoo(
        self,
        symbol: str,
        include_after_hours: bool,
        include_premarket: bool,
        include_live: bool
    ) -> NormalizedDataResult:
        """Get price data from Yahoo Finance"""
        try:
            # Get official close
            official_close_data = await self.yahoo.get_official_close(symbol)
            if not official_close_data:
                return NormalizedDataResult(success=False, error="No official close data")
            
            official_close = OfficialClose(
                price=official_close_data.get("price", 0),
                change=official_close_data.get("change", 0),
                change_percent=official_close_data.get("change_percent", 0),
                timestamp=official_close_data.get("timestamp"),
                source="yahoo"
            )
            
            # Get after-hours price
            after_hours = AfterHoursData(price=0, change=0, change_percent=0, source=None, timestamp=None)
            if include_after_hours:
                ah_price = await self.yahoo.get_after_hours_price(symbol)
                if ah_price:
                    change = ah_price.get("price", 0) - official_close.price
                    change_percent = (change / official_close.price * 100) if official_close.price > 0 else 0
                    after_hours = AfterHoursData(
                        price=ah_price.get("price", 0),
                        change=change,
                        change_percent=change_percent,
                        source="yahoo",
                        timestamp=ah_price.get("timestamp")
                    )
            
            # Premarket data
            premarket = PremarketData(price=0, change=0, change_percent=0, source=None, timestamp=None)
            if include_premarket:
                # Yahoo provides premarket in TickerInfo
                # Simplified - would need additional API calls
                pass
            
            # Live data
            live = None
            if include_live:
                # Yahoo doesn't provide true live data, use after-hours for now
                live = LiveData(
                    price=after_hours.price if after_hours.price > 0 else official_close.price,
                    change=after_hours.change if after_hours.price > 0 else 0,
                    change_percent=after_hours.change_percent if after_hours.price > 0 else 0,
                    bid=0,
                    ask=0,
                    bid_size=0,
                    ask_size=0,
                    volume=0,
                    high=0,
                    low=0,
                    open=0,
                    source="yahoo",
                    timestamp=datetime.now()
                )
            
            differences = {}
            if after_hours.price > 0:
                differences["after_hours_vs_close"] = after_hours.price - official_close.price
            
            data = TickerPriceData(
                symbol=symbol,
                official_close=official_close,
                after_hours=after_hours,
                premarket=premarket,
                live=live,
                opening_range=OpeningRange(high=0, low=0, calculated_at=None),
                vwap=VWAP(price=0, calculated_at=None),
                differences=differences,
                last_updated=datetime.now(),
                data_quality="high",
                session_type=SessionType.LIVE if include_live else SessionType.PRE_MARKET
            )
            
            return NormalizedDataResult(success=True, data=data)
            
        except Exception as e:
            logger.error(f"Yahoo price data error: {str(e)}")
            return NormalizedDataResult(success=False, error=str(e))
    
    async def _get_price_from_alpha_vantage(
        self,
        symbol: str,
        include_after_hours: bool,
        include_premarket: bool,
        include_live: bool
    ) -> NormalizedDataResult:
        """Get price data from Alpha Vantage (fallback)"""
        try:
            # Alpha Vantage provides delayed quotes (15-20 min)
            quote = await self.alpha_vantage.get_quote(symbol)
            if not quote:
                return NormalizedDataResult(success=False, error="No quote data")
            
            official_close = OfficialClose(
                price=quote.get("prev_close", 0),
                change=0,
                change_percent=0,
                timestamp=datetime.now() - timedelta(days=1),
                source="alpha_vantage"
            )
            
            # Use current quote as "after hours" for premarket analysis
            after_hours = AfterHoursData(
                price=quote.get("price", 0),
                change=quote.get("change", 0),
                change_percent=quote.get("change_percent", 0),
                source="alpha_vantage",
                timestamp=quote.get("timestamp")
            )
            
            data = TickerPriceData(
                symbol=symbol,
                official_close=official_close,
                after_hours=after_hours,
                premarket=PremarketData(price=0, change=0, change_percent=0, source=None, timestamp=None),
                live=LiveData(
                    price=quote.get("price", 0),
                    change=quote.get("change", 0),
                    change_percent=quote.get("change_percent", 0),
                    bid=0,
                    ask=0,
                    bid_size=0,
                    ask_size=0,
                    volume=quote.get("volume", 0),
                    high=quote.get("high", 0),
                    low=quote.get("low", 0),
                    open=quote.get("open", 0),
                    source="alpha_vantage",
                    timestamp=quote.get("timestamp")
                ) if include_live else None,
                opening_range=OpeningRange(high=0, low=0, calculated_at=None),
                vwap=VWAP(price=0, calculated_at=None),
                differences={
                    "after_hours_vs_close": after_hours.price - official_close.price
                },
                last_updated=datetime.now(),
                data_quality="medium",  # Delayed data
                session_type=SessionType.LIVE if include_live else SessionType.PRE_MARKET
            )
            
            return NormalizedDataResult(success=True, data=data)
            
        except Exception as e:
            logger.error(f"Alpha Vantage price data error: {str(e)}")
            return NormalizedDataResult(success=False, error=str(e))
    
    async def get_normalized_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1d",
        limit: int = 100
    ) -> NormalizedDataResult:
        """
        Get normalized OHLCV data from best available source
        
        Args:
            symbol: Stock symbol
            timeframe: Timeframe (1d, 15m, 1h)
            limit: Number of candles
        
        Returns:
            NormalizedDataResult with OHLCVSeries
        """
        warnings = []
        
        for source_name in self.ohlcv_source_priority:
            try:
                if source_name == "yahoo" and self.yahoo:
                    result = await self._get_ohlcv_from_yahoo(symbol, timeframe, limit)
                elif source_name == "alpha_vantage" and self.alpha_vantage:
                    result = await self._get_ohlcv_from_alpha_vantage(symbol, timeframe, limit)
                else:
                    continue
                
                if result.success:
                    result.source = source_name
                    result.warnings = warnings
                    return result
                else:
                    warnings.append(f"{source_name}: {result.error}")
                    
            except Exception as e:
                logger.warning(f"{source_name} OHLCV failed for {symbol}: {str(e)}")
                warnings.append(f"{source_name}: {str(e)}")
                continue
        
        return NormalizedDataResult(
            success=False,
            error=f"All sources failed for {symbol} OHLCV",
            warnings=warnings
        )
    
    async def _get_ohlcv_from_yahoo(
        self,
        symbol: str,
        timeframe: str,
        limit: int
    ) -> NormalizedDataResult:
        """Get OHLCV from Yahoo Finance"""
        try:
            # Map timeframe to Yahoo intervals
            timeframe_map = {
                "15m": "15m",
                "1h": "1h",
                "1d": "1d"
            }
            interval = timeframe_map.get(timeframe, "1d")
            
            # Get OHLCV data
            ohlcv_raw = await self.yahoo.get_ohlcv(symbol, interval, limit)
            if not ohlcv_raw:
                return NormalizedDataResult(success=False, error="No OHLCV data")
            
            # Convert to OHLCVCandle objects
            candles = []
            for raw_candle in ohlcv_raw:
                candle = OHLCVCandle(
                    timestamp=raw_candle.get("timestamp", datetime.now()),
                    open=raw_candle.get("open", 0),
                    high=raw_candle.get("high", 0),
                    low=raw_candle.get("low", 0),
                    close=raw_candle.get("close", 0),
                    volume=raw_candle.get("volume", 0)
                )
                candles.append(candle)
            
            ohlcv_series = OHLCVSeries(
                symbol=symbol,
                timeframe=timeframe,
                candles=candles,
                last_updated=datetime.now()
            )
            
            return NormalizedDataResult(success=True, data=ohlcv_series)
            
        except Exception as e:
            logger.error(f"Yahoo OHLCV error: {str(e)}")
            return NormalizedDataResult(success=False, error=str(e))
    
    async def _get_ohlcv_from_alpha_vantage(
        self,
        symbol: str,
        timeframe: str,
        limit: int
    ) -> NormalizedDataResult:
        """Get OHLCV from Alpha Vantage"""
        try:
            # Get data from Alpha Vantage
            if timeframe == "1d":
                ohlcv_raw = await self.alpha_vantage.get_daily_ohlcv(symbol, outputsize="compact")
            else:
                # Map timeframe to AV intervals
                interval_map = {
                    "15m": "15min",
                    "1h": "60min"
                }
                interval = interval_map.get(timeframe, "15min")
                ohlcv_raw = await self.alpha_vantage.get_intraday_ohlcv(symbol, interval)
            
            if not ohlcv_raw:
                return NormalizedDataResult(success=False, error="No OHLCV data")
            
            # Convert to OHLCVCandle objects
            candles = []
            for raw_candle in ohlcv_raw[:limit]:  # Limit candles
                candle = OHLCVCandle(
                    timestamp=raw_candle.get("timestamp", datetime.now()),
                    open=raw_candle.get("open", 0),
                    high=raw_candle.get("high", 0),
                    low=raw_candle.get("low", 0),
                    close=raw_candle.get("close", 0),
                    volume=raw_candle.get("volume", 0)
                )
                candles.append(candle)
            
            ohlcv_series = OHLCVSeries(
                symbol=symbol,
                timeframe=timeframe,
                candles=candles,
                last_updated=datetime.now()
            )
            
            return NormalizedDataResult(success=True, data=ohlcv_series)
            
        except Exception as e:
            logger.error(f"Alpha Vantage OHLCV error: {str(e)}")
            return NormalizedDataResult(success=False, error=str(e))
    
    async def get_catalyst_data(
        self,
        symbol: str,
        days_back: int = 7
    ) -> NormalizedDataResult:
        """
        Get catalyst data (news, earnings, events)
        
        Args:
            symbol: Stock symbol
            days_back: Number of days to look back
        
        Returns:
            NormalizedDataResult with catalyst data
        """
        if not self.finnhub:
            return NormalizedDataResult(success=False, error="Finnhub client not configured")
        
        try:
            # Get company news
            news = await self.finnhub.get_company_news(symbol, days_back)
            
            # Get recent developments
            developments = await self.finnhub.get_major_developments(symbol, days_back)
            
            catalyst_data = {
                "symbol": symbol,
                "news": news or [],
                "developments": developments or [],
                "recent_news_count": len(news) if news else 0,
                "has_recent_catalysts": bool(news or developments)
            }
            
            return NormalizedDataResult(success=True, data=catalyst_data, source="finnhub")
            
        except Exception as e:
            logger.error(f"Catalyst data error: {str(e)}")
            return NormalizedDataResult(success=False, error=str(e))