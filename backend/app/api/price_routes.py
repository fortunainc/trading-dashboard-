"""
Price Data API Routes
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
import logging

from ..models.price_data import TickerPriceData, OfficialClose, PreviousDayContext
from ..models.ohlcv import OHLCVSeries, OHLCVCandle

logger = logging.getLogger(__name__)

router = APIRouter()


# Mock data for demonstration (will be replaced with real data fetching)
@router.get("/{symbol}")
async def get_price_data(
    symbol: str,
    include_ohlcv: bool = Query(False, description="Include OHLCV data")
) -> dict:
    """
    Get complete price data for a ticker
    
    Returns four separate price types:
    - official_close: Previous day regular session close
    - after_hours: After-hours trading price
    - premarket: Pre-market trading price
    - live: Current live price
    """
    try:
        # Mock data - will be replaced with real data fetching in Phase 2
        mock_price = 500.00
        
        price_data = {
            "symbol": symbol,
            "official_close": {
                "price": mock_price,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "is_regular_session": True,
                "source": "Yahoo Finance"
            },
            "after_hours": {
                "price": None,
                "change_from_close": None,
                "change_percent": None,
                "timestamp": None,
                "source": "Tradier"
            },
            "premarket": {
                "price": None,
                "change_from_close": None,
                "change_percent": None,
                "timestamp": None,
                "source": "Tradier"
            },
            "live": {
                "price": mock_price + 2.50,
                "change_from_close": 2.50,
                "change_percent": 0.50,
                "timestamp": datetime.now().isoformat(),
                "source": "Tradier"
            },
            "opening_range": {
                "high": mock_price + 1.00,
                "low": mock_price - 0.50,
                "midpoint": mock_price + 0.25
            },
            "vwap": {
                "price": mock_price + 0.75
            },
            "differences": {
                "after_hours_vs_close": None,
                "premarket_vs_close": None,
                "live_vs_close": 2.50,
                "premarket_vs_after_hours": None,
                "live_vs_premarket": None
            },
            "last_updated": datetime.now().isoformat(),
            "data_quality": "good",
            "session_type": "regular"
        }
        
        if include_ohlcv:
            price_data["ohlcv"] = {
                "15m": _generate_mock_ohlcv(symbol, "15m", 20),
                "1h": _generate_mock_ohlcv(symbol, "1h", 10),
                "4h": _generate_mock_ohlcv(symbol, "4h", 5),
                "d": _generate_mock_ohlcv(symbol, "d", 10)
            }
        
        return price_data
    
    except Exception as e:
        logger.error(f"Error fetching price data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/batch")
async def get_batch_price_data(
    symbols: str = Query(..., description="Comma-separated list of symbols")
) -> List[dict]:
    """
    Get price data for multiple tickers
    """
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
        results = []
        
        for symbol in symbol_list:
            price_data = await get_price_data(symbol, include_ohlcv=False)
            results.append(price_data)
        
        return results
    
    except Exception as e:
        logger.error(f"Error fetching batch price data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _generate_mock_ohlcv(symbol: str, timeframe: str, count: int) -> dict:
    """Generate mock OHLCV data for demonstration"""
    base_price = 500.00
    candles = []
    
    for i in range(count):
        candles.append({
            "timestamp": datetime.now().isoformat(),
            "open": round(base_price + (i * 0.5), 2),
            "high": round(base_price + (i * 0.5) + 1.0, 2),
            "low": round(base_price + (i * 0.5) - 0.5, 2),
            "close": round(base_price + (i * 0.5) + 0.25, 2),
            "volume": 1000000 + (i * 10000)
        })
    
    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "candles": candles
    }