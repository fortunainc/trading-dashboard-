"""
Yahoo Finance Client for official close data
"""
import yfinance as yf
from typing import Optional, Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class YahooClient:
    """Client for Yahoo Finance data - primary source for official close"""
    
    def __init__(self):
        pass
    
    async def get_official_close(self, symbol: str) -> Optional[Dict]:
        """
        Get official close price for the previous regular session
        
        Returns:
            Dict with price, date, volume, etc.
        """
        try:
            ticker = yf.Ticker(symbol)
            
            # Get the most recent trading day's data
            hist = ticker.history(period="2d")
            
            if len(hist) == 0:
                logger.error(f"No data found for {symbol}")
                return None
            
            # Get the most recent complete day (yesterday if market is closed)
            latest = hist.iloc[-1]
            
            return {
                'symbol': symbol,
                'price': float(latest['Close']),
                'open': float(latest['Open']),
                'high': float(latest['High']),
                'low': float(latest['Low']),
                'volume': int(latest['Volume']),
                'date': latest.name.strftime('%Y-%m-%d'),
                'is_regular_session': True,
                'source': 'Yahoo Finance'
            }
        except Exception as e:
            logger.error(f"Error fetching official close from Yahoo for {symbol}: {e}")
            return None
    
    async def get_previous_day_context(self, symbol: str) -> Optional[Dict]:
        """
        Get previous day's context (close, high, low, volume)
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")
            
            if len(hist) < 2:
                logger.error(f"Insufficient data for {symbol}")
                return None
            
            # Previous close = second to last candle
            prev_day = hist.iloc[-2]
            
            return {
                'symbol': symbol,
                'previous_close': float(prev_day['Close']),
                'high': float(prev_day['High']),
                'low': float(prev_day['Low']),
                'volume': int(prev_day['Volume']),
                'date': prev_day.name.strftime('%Y-%m-%d')
            }
        except Exception as e:
            logger.error(f"Error fetching previous day context from Yahoo for {symbol}: {e}")
            return None
    
    async def get_ohlcv(
        self,
        symbol: str,
        interval: str = "15m",
        period: str = "5d"
    ) -> Optional[list]:
        """
        Get OHLCV data
        
        Args:
            symbol: Stock symbol
            interval: '1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo'
            period: '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'
            
        Returns:
            List of OHLCV candles
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval=interval)
            
            if len(hist) == 0:
                logger.error(f"No OHLCV data found for {symbol}")
                return None
            
            candles = []
            for idx, row in hist.iterrows():
                candles.append({
                    'timestamp': idx,
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume'])
                })
            
            return candles
        except Exception as e:
            logger.error(f"Error fetching OHLCV from Yahoo for {symbol}: {e}")
            return None
    
    async def get_after_hours_price(self, symbol: str) -> Optional[Dict]:
        """
        Get after-hours price (if market is still in after-hours session)
        
        Note: Yahoo Finance may have delayed after-hours data
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d", interval="1m")
            
            if len(hist) == 0:
                return None
            
            # Last available price
            latest = hist.iloc[-1]
            
            return {
                'symbol': symbol,
                'price': float(latest['Close']),
                'timestamp': latest.name,
                'source': 'Yahoo Finance'
            }
        except Exception as e:
            logger.error(f"Error fetching after-hours price from Yahoo for {symbol}: {e}")
            return None