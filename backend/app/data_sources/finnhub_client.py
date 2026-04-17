"""
Finnhub Client - Catalyst Data Source
Provides earnings data, news, and company events for catalyst tracking
"""

import httpx
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class FinnhubClient:
    """Client for Finnhub API - catalyst and events data"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://finnhub.io/api/v1"
        self.timeout = 30.0
        
    async def get_company_news(
        self,
        symbol: str,
        days_back: int = 7
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get recent company news
        
        Args:
            symbol: Stock symbol
            days_back: Number of days to look back
        
        Returns:
            List of news articles or None if error
        """
        try:
            to_date = datetime.now()
            from_date = to_date - timedelta(days=days_back)
            
            params = {
                "symbol": symbol,
                "from": from_date.strftime("%Y-%m-%d"),
                "to": to_date.strftime("%Y-%m-%d"),
                "token": self.api_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/news",
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                news_data = response.json()
                
                if not isinstance(news_data, list):
                    logger.error(f"Invalid Finnhub news response for {symbol}")
                    return None
                
                # Parse and filter news
                news_list = []
                for article in news_data:
                    news_list.append({
                        "datetime": datetime.fromtimestamp(article["datetime"]),
                        "headline": article["headline"],
                        "source": article["source"],
                        "url": article["url"],
                        "summary": article["summary"],
                        "related": article["related"]
                    })
                
                return news_list
                
        except httpx.TimeoutException:
            logger.error(f"Finnhub timeout for {symbol} news")
            return None
        except Exception as e:
            logger.error(f"Finnhub error for {symbol} news: {str(e)}")
            return None
    
    async def get_company_basic_financials(
        self, symbol: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get basic company financials
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Financial data or None if error
        """
        try:
            params = {
                "symbol": symbol,
                "token": self.api_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/stock/metric",
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                data = response.json()
                
                if "metric" not in data:
                    logger.error(f"Invalid Finnhub financials response for {symbol}")
                    return None
                
                metrics = data["metric"]
                
                return {
                    "symbol": symbol,
                    "market_cap": metrics.get("marketCapitalization"),
                    "pe_ratio": metrics.get("peBasicExclExtraTTM"),
                    "pb_ratio": metrics.get("pbQuarterly"),
                    "dividend_yield": metrics.get("dividendYieldIndicatedAnnual"),
                    "eps": metrics.get("epsTTM"),
                    "revenue": metrics.get("totalRevenue"),
                    "profit_margin": metrics.get("netProfitMarginTTM"),
                    "roe": metrics.get("roeTTM"),
                    "debt_to_equity": metrics.get("debtToEquityQuarterly")
                }
                
        except httpx.TimeoutException:
            logger.error(f"Finnhub timeout for {symbol} financials")
            return None
        except Exception as e:
            logger.error(f"Finnhub error for {symbol} financials: {str(e)}")
            return None
    
    async def get_company_profile(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get company profile information
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Company profile or None if error
        """
        try:
            params = {
                "symbol": symbol,
                "token": self.api_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/stock/profile2",
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                data = response.json()
                
                if not data:
                    logger.error(f"No company profile found for {symbol}")
                    return None
                
                return {
                    "symbol": symbol,
                    "name": data.get("name"),
                    "industry": data.get("gics"),
                    "sector": data.get("sector"),
                    "country": data.get("country"),
                    "currency": data.get("currency"),
                    "exchange": data.get("exchange"),
                    "ipo": datetime.strptime(data["ipo"], "%Y-%m-%d") if data.get("ipo") else None,
                    "market_cap": data.get("marketCapitalization"),
                    "shares_outstanding": data.get("shareOutstanding"),
                    "website": data.get("weburl"),
                    "logo": data.get("logo")
                }
                
        except httpx.TimeoutException:
            logger.error(f"Finnhub timeout for {symbol} profile")
            return None
        except Exception as e:
            logger.error(f"Finnhub error for {symbol} profile: {str(e)}")
            return None
    
    async def get_major_developments(
        self,
        symbol: str,
        days_back: int = 30
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get major developments (press releases, SEC filings)
        
        Args:
            symbol: Stock symbol
            days_back: Number of days to look back
        
        Returns:
            List of developments or None if error
        """
        try:
            from_date = int((datetime.now() - timedelta(days=days_back)).timestamp())
            
            params = {
                "symbol": symbol,
                "from": from_date,
                "token": self.api_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/press-releases",
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                data = response.json()
                
                if not isinstance(data, list):
                    logger.error(f"Invalid Finnhub developments response for {symbol}")
                    return None
                
                developments = []
                for item in data:
                    developments.append({
                        "datetime": datetime.fromtimestamp(item["datetime"]),
                        "headline": item["headline"],
                        "url": item["url"],
                        "source": item["source"]
                    })
                
                return developments
                
        except httpx.TimeoutException:
            logger.error(f"Finnhub timeout for {symbol} developments")
            return None
        except Exception as e:
            logger.error(f"Finnhub error for {symbol} developments: {str(e)}")
            return None
    
    async def check_trading_status(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Check if symbol is trading
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Trading status or None if error
        """
        try:
            params = {
                "symbol": symbol,
                "token": self.api_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/stock/symbol",
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                data = response.json()
                
                if not isinstance(data, list) or len(data) == 0:
                    logger.error(f"No trading status found for {symbol}")
                    return None
                
                symbol_data = data[0]
                
                return {
                    "symbol": symbol,
                    "description": symbol_data.get("description"),
                    "type": symbol_data.get("type"),  # Common Stock, ETF, etc.
                    "exchange": symbol_data.get("displaySymbol"),
                    "currency": symbol_data.get("currency"),
                    "is_trading": symbol_data.get("type") in ["Common Stock", "ETF", "REIT"]
                }
                
        except httpx.TimeoutException:
            logger.error(f"Finnhub timeout for {symbol} trading status")
            return None
        except Exception as e:
            logger.error(f"Finnhub error for {symbol} trading status: {str(e)}")
            return None