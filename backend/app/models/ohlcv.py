"""
OHLCV Data Models for technical analysis
"""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class OHLCVCandle:
    """Individual OHLCV candle"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    
    def to_dict(self) -> dict:
        return {
            'timestamp': self.timestamp,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume
        }


@dataclass
class OHLCVSeries:
    """Series of OHLCV candles for a specific timeframe"""
    timeframe: str  # '1m', '5m', '15m', '1h', '4h', 'd', 'w'
    candles: List[OHLCVCandle]
    symbol: str
    
    def get_latest_candle(self) -> Optional[OHLCVCandle]:
        """Get the most recent candle"""
        return self.candles[-1] if self.candles else None
    
    def get_candles_count(self, n: int) -> List[OHLCVCandle]:
        """Get last N candles"""
        return self.candles[-n:] if len(self.candles) >= n else self.candles
    
    def get_highs(self, n: int = None) -> List[float]:
        """Get list of high prices"""
        candles = self.get_candles_count(n) if n else self.candles
        return [c.high for c in candles]
    
    def get_lows(self, n: int = None) -> List[float]:
        """Get list of low prices"""
        candles = self.get_candles_count(n) if n else self.candles
        return [c.low for c in candles]
    
    def get_closes(self, n: int = None) -> List[float]:
        """Get list of close prices"""
        candles = self.get_candles_count(n) if n else self.candles
        return [c.close for c in candles]
    
    def get_volumes(self, n: int = None) -> List[int]:
        """Get list of volumes"""
        candles = self.get_candles_count(n) if n else self.candles
        return [c.volume for c in candles]