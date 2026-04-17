"""
IV Filter - Filter based on Implied Volatility
"""
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class IVFilter:
    """
    Hard Filter: Implied Volatility
    
    Rejects tickers with extreme IV levels
    """
    
    def __init__(self):
        self.min_iv_rank = 10  # Minimum 10 IV Rank
        self.max_iv_rank = 90  # Maximum 90 IV Rank
    
    def filter(
        self,
        symbol: str,
        iv_rank: Optional[float] = None,
        iv_percentile: Optional[float] = None
    ) -> Dict:
        """
        Filter ticker based on IV
        
        Args:
            symbol: Ticker symbol
            iv_rank: IV Rank (0-100)
            iv_percentile: IV Percentile (0-100)
            
        Returns:
            Dict with 'pass' status and reason
        """
        # Use whichever IV metric is available
        iv_value = iv_rank if iv_rank is not None else iv_percentile
        
        if iv_value is None:
            return {
                'pass': True,  # Don't filter if no IV data available
                'reason': f"{symbol}: IV data not available, skipping IV filter"
            }
        
        if iv_value < self.min_iv_rank:
            return {
                'pass': False,
                'reason': f"{symbol}: IV too low - {iv_value:.1f} (min {self.min_iv_rank})"
            }
        
        if iv_value > self.max_iv_rank:
            return {
                'pass': False,
                'reason': f"{symbol}: IV too high - {iv_value:.1f} (max {self.max_iv_rank})"
            }
        
        return {
            'pass': True,
            'reason': f"{symbol}: IV {iv_value:.1f} is in acceptable range"
        }