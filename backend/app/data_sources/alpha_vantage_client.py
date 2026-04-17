"""
Alpha Vantage Client - Fallback Data Source
Provides historical data as backup when primary sources fail
"""

import httpx
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class AlphaVantageClient:
    """Client for Alpha Vantage API - fallback data source"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
        self.timeout = 30.0
        self.rate_limit_delay = 12.0  # 5 calls per minute limit
        
    async def get_daily_ohlcv(
        self, 
        symbol: str, 
        outputsize: str = "compact"
    ) -> Optional[List[Dict]]:
        """
        Get daily OHLCV data
        
        Args:
            symbol: Stock symbol
            outputsize: 'compact' (last 100 days) or 'full' (20+ years)
        
        Returns:
            List of OHLCV candles or None if error
        """
        try:
            params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": symbol,
                "outputsize": outputsize,
                "apikey": self.api_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.base_url,
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                data = response.json()
                
                # Check for error messages
                if "Error Message" in data:
                    logger.error(f"Alpha Vantage error for {symbol}: {data['Error Message']}")
                    return None
                
                if "Note" in data:
                    logger.warning(f"Alpha Vantage rate limit: {data['Note']}")
                    return None
                
                if "Time Series (Daily)" not in data:
                    logger.error(f"Invalid Alpha Vantage response for {symbol}")
                    return None
                
                # Parse OHLCV data
                time_series = data["Time Series (Daily)"]
                ohlcv_data = []
                
                for date_str, candle_data in time_series.items():
                    candle = {
                        "timestamp": datetime.strptime(date_str, "%Y-%m-%d"),
                        "open": float(candle_data["1. open"]),
                        "high": float(candle_data["2. high"]),
                        "low": float(candle_data["3. low"]),
                        "close": float(candle_data["4. close"]),
                        "volume": int(candle_data["5. volume"])
                    }
                    ohlcv_data.append(candle)
                
                # Sort by timestamp descending
                ohlcv_data.sort(key=lambda x: x["timestamp"], reverse=True)
                
                return ohlcv_data
                
        except httpx.TimeoutException:
            logger.error(f"Alpha Vantage timeout for {symbol}")
            return None
        except Exception as e:
            logger.error(f"Alpha Vantage error for {symbol}: {str(e)}")
            return None
    
    async def get_intraday_ohlcv(
        self,
        symbol: str,
        interval: str = "15min"
    ) -> Optional[List[Dict]]:
        """
        Get intraday OHLCV data
        
        Args:
            symbol: Stock symbol
            interval: '1min', '5min', '15min', '30min', '60min'
        
        Returns:
            List of OHLCV candles or None if error
        """
        try:
            params = {
                "function": "TIME_SERIES_INTRADAY",
                "symbol": symbol,
                "interval": interval,
                "outputsize": "full",
                "apikey": self.api_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.base_url,
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                data = response.json()
                
                # Check for error messages
                if "Error Message" in data:
                    logger.error(f"Alpha Vantage error for {symbol}: {data['Error Message']}")
                    return None
                
                if "Note" in data:
                    logger.warning(f"Alpha Vantage rate limit: {data['Note']}")
                    return None
                
                time_series_key = f"Time Series ({interval})"
                if time_series_key not in data:
                    logger.error(f"Invalid Alpha Vantage response for {symbol}")
                    return None
                
                # Parse OHLCV data
                time_series = data[time_series_key]
                ohlcv_data = []
                
                for date_str, candle_data in time_series.items():
                    candle = {
                        "timestamp": datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S"),
                        "open": float(candle_data["1. open"]),
                        "high": float(candle_data["2. high"]),
                        "low": float(candle_data["3. low"]),
                        "close": float(candle_data["4. close"]),
                        "volume": int(candle_data["5. volume"])
                    }
                    ohlcv_data.append(candle)
                
                # Sort by timestamp descending
                ohlcv_data.sort(key=lambda x: x["timestamp"], reverse=True)
                
                return ohlcv_data
                
        except httpx.TimeoutException:
            logger.error(f"Alpha Vantage timeout for {symbol}")
            return None
        except Exception as e:
            logger.error(f"Alpha Vantage error for {symbol}: {str(e)}")
            return None
    
    async def get_quote(self, symbol: str) -> Optional[Dict]:
        """
        Get real-time quote (delayed by free tier)
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Quote data or None if error
        """
        try:
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": self.api_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.base_url,
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                data = response.json()
                
                # Check for error messages
                if "Error Message" in data:
                    logger.error(f"Alpha Vantage error for {symbol}: {data['Error Message']}")
                    return None
                
                if "Note" in data:
                    logger.warning(f"Alpha Vantage rate limit: {data['Note']}")
                    return None
                
                if "Global Quote" not in data:
                    logger.error(f"Invalid Alpha Vantage response for {symbol}")
                    return None
                
                quote_data = data["Global Quote"]
                
                return {
                    "symbol": symbol,
                    "price": float(quote_data["05. price"]),
                    "change": float(quote_data["09. change"]),
                    "change_percent": float(quote_data["10. change percent"].replace("%", "")),
                    "volume": int(quote_data["06. volume"]),
                    "prev_close": float(quote_data["08. previous close"]),
                    "open": float(quote_data["02. open"]),
                    "high": float(quote_data["03. high"]),
                    "low": float(quote_data["04. low"]),
                    "timestamp": datetime.now()
                }
                
        except httpx.TimeoutException:
            logger.error(f"Alpha Vantage timeout for {symbol}")
            return None
        except Exception as e:
            logger.error(f"Alpha Vantage error for {symbol}: {str(e)}")
            return None