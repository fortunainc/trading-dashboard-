"""
Tradier API Client for real-time options data and live prices
"""
import httpx
from typing import Dict, List, Optional
from datetime import datetime
from ..config import settings
import logging

logger = logging.getLogger(__name__)


class TradierClient:
    """Client for Tradier API"""
    
    def __init__(self):
        self.api_key = settings.tradier_api_key
        self.base_url = settings.tradier_api_url
        self.timeout = settings.tradier_timeout
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Accept': 'application/json'
        }
        self.client = httpx.AsyncClient(headers=self.headers, timeout=self.timeout)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def get_quote(self, symbol: str) -> Optional[Dict]:
        """
        Get real-time quote for a symbol
        
        Returns quote data including:
        - last (live price)
        - bid
        - ask
        - volume
        - open_interest (for options)
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/markets/quotes",
                params={'symbols': symbol}
            )
            response.raise_for_status()
            data = response.json()
            
            if data['quotes']['quote']:
                return data['quotes']['quote']
            return None
        except Exception as e:
            logger.error(f"Error fetching quote from Tradier for {symbol}: {e}")
            return None
    
    async def get_option_chain(self, symbol: str, expiration: str = None) -> Optional[Dict]:
        """
        Get option chain for a symbol
        
        Args:
            symbol: Stock symbol
            expiration: Expiration date (YYYY-MM-DD), if None gets all expirations
            
        Returns:
            Option chain data with calls and puts
        """
        try:
            params = {'symbol': symbol}
            if expiration:
                params['expiration'] = expiration
            
            response = await self.client.get(
                f"{self.base_url}/markets/options/chains",
                params=params
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching option chain from Tradier for {symbol}: {e}")
            return None
    
    async def get_expirations(self, symbol: str) -> Optional[List[str]]:
        """Get available expiration dates for options"""
        try:
            response = await self.client.get(
                f"{self.base_url}/markets/options/expirations",
                params={'symbol': symbol}
            )
            response.raise_for_status()
            data = response.json()
            
            if 'expirations' in data and 'date' in data['expirations']:
                return data['expirations']['date']
            return None
        except Exception as e:
            logger.error(f"Error fetching expirations from Tradier for {symbol}: {e}")
            return None
    
    async def get_historical_quotes(
        self,
        symbol: str,
        start: str,
        end: str,
        interval: str = "15min"
    ) -> Optional[Dict]:
        """
        Get historical quotes (OHLCV)
        
        Args:
            symbol: Stock symbol
            start: Start date (YYYY-MM-DD)
            end: End date (YYYY-MM-DD)
            interval: Interval (1min, 5min, 15min, 1hour, 1day, 1week)
            
        Returns:
            Historical OHLCV data
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/markets/timesales",
                params={
                    'symbol': symbol,
                    'start': start,
                    'end': end,
                    'interval': interval
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching historical quotes from Tradier for {symbol}: {e}")
            return None
    
    def get_iv_rank(self, symbol: str) -> Optional[float]:
        """
        Calculate IV rank for a symbol
        
        IV Rank = (Current IV - 1 Year Low IV) / (1 Year High IV - 1 Year Low IV)
        
        Note: This requires historical IV data, which may not be directly available
        This is a placeholder - would need historical option data
        """
        # TODO: Implement with historical IV data
        return None