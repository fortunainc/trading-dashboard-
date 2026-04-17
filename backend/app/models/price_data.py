"""
MASTER PRICE DATA MODEL
Explicitly separates four price types: official_close, after_hours, premarket, live
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum


class SessionType(str, Enum):
    REGULAR = "regular"
    PREMARKET = "premarket"
    AFTER_HOURS = "after_hours"
    CLOSED = "closed"


@dataclass
class OfficialClose:
    """Official regular session close data from Yahoo Finance"""
    price: float
    date: str
    is_regular_session: bool
    source: str


@dataclass
class PreviousDayContext:
    """Previous day's context for comparison"""
    previous_close: float
    high: float
    low: float
    volume: int


@dataclass
class AfterHoursData:
    """After-hours trading data"""
    price: Optional[float]
    change_from_close: Optional[float]
    change_percent: Optional[float]
    timestamp: Optional[datetime]
    source: str


@dataclass
class PremarketData:
    """Pre-market trading data"""
    price: Optional[float]
    change_from_close: Optional[float]
    change_percent: Optional[float]
    timestamp: Optional[datetime]
    source: str


@dataclass
class LiveData:
    """Live market data"""
    price: Optional[float]
    change_from_close: Optional[float]
    change_percent: Optional[float]
    timestamp: Optional[datetime]
    source: str


@dataclass
class OpeningRange:
    """Opening range data (first 15 minutes)"""
    high: Optional[float]
    low: Optional[float]
    midpoint: Optional[float]


@dataclass
class VWAP:
    """Volume Weighted Average Price"""
    price: Optional[float]


@dataclass
class MarketOpen:
    """Market open gap data"""
    gap_percent: float
    gap_type: str  # 'bullish', 'bearish', 'flat'


@dataclass
class TickerPriceData:
    """
    MASTER TICKER PRICE DATA MODEL
    All four price types are explicitly separated - NO COLLAPSE
    """
    symbol: str
    official_close: OfficialClose
    previous_day: PreviousDayContext
    after_hours: AfterHoursData
    premarket: PremarketData
    live: LiveData
    opening_range: OpeningRange
    vwap: VWAP
    market_open: Optional[MarketOpen]
    differences: dict
    last_updated: datetime
    data_quality: str
    session_type: SessionType
    
    def __post_init__(self):
        """Calculate differences between price types"""
        self.differences = {
            'after_hours_vs_close': self._calculate_diff(
                self.after_hours.price, self.official_close.price
            ),
            'premarket_vs_close': self._calculate_diff(
                self.premarket.price, self.official_close.price
            ),
            'live_vs_close': self._calculate_diff(
                self.live.price, self.official_close.price
            ),
            'premarket_vs_after_hours': self._calculate_diff(
                self.premarket.price, self.after_hours.price
            ),
            'live_vs_premarket': self._calculate_diff(
                self.live.price, self.premarket.price
            ),
        }
    
    @staticmethod
    def _calculate_diff(current: Optional[float], base: Optional[float]) -> Optional[float]:
        """Calculate difference between two prices"""
        if current is None or base is None:
            return None
        return current - base