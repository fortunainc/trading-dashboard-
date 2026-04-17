"""
Gap Risk Filter - Filter based on overnight gap risk
"""
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class GapRiskFilter:
    """
    Hard Filter: Gap Risk
    
    Rejects tickers with high overnight gap risk
    """
    
    def __init__(self):
        self.max_gap_percent = 5.0  # Maximum 5% gap
    
    def filter(
        self,
        symbol: str,
        premarket_price: Optional[float] = None,
        previous_close: Optional[float] = None,
        earnings_upcoming: bool = False
    ) -> Dict:
        """
        Filter ticker based on gap risk
        
        Args:
            symbol: Ticker symbol
            premarket_price: Premarket price
            previous_close: Previous day close
            earnings_upcoming: Whether earnings are upcoming
            
        Returns:
            Dict with 'pass' status and reason
        """
        # Check for upcoming earnings
        if earnings_upcoming:
            return {
                'pass': False,
                'reason': f"{symbol}: High gap risk - earnings upcoming"
            }
        
        # Calculate gap if both prices available
        if premarket_price is not None and previous_close is not None:
            if previous_close == 0:
                return {
                    'pass': False,
                    'reason': f"{symbol}: Previous close is zero"
                }
            
            gap_percent = abs((premarket_price - previous_close) / previous_close) * 100
            
            if gap_percent > self.max_gap_percent:
                return {
                    'pass': False,
                    'reason': f"{symbol}: Gap risk too high - {gap_percent:.2f}% gap (max {self.max_gap_percent}%)"
                }
        
        return {
            'pass': True,
            'reason': f"{symbol}: Gap risk is acceptable"
        }