"""
Spread Filter - Filter based on bid/ask spread
"""
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class SpreadFilter:
    """
    Hard Filter: Bid/Ask Spread
    
    Rejects tickers with excessive bid/ask spreads
    """
    
    def __init__(self):
        self.max_spread_percent_scalp = 10.0   # 10% for scalp
        self.max_spread_percent_swing = 5.0    # 5% for swing
    
    def filter(
        self,
        symbol: str,
        bid: Optional[float] = None,
        ask: Optional[float] = None,
        setup_type: str = 'scalp'
    ) -> Dict:
        """
        Filter ticker based on bid/ask spread
        
        Args:
            symbol: Ticker symbol
            bid: Bid price
            ask: Ask price
            setup_type: 'scalp' or 'swing'
            
        Returns:
            Dict with 'pass' status and reason
        """
        if bid is None or ask is None or bid == 0:
            return {
                'pass': False,
                'reason': f"{symbol}: Spread data not available"
            }
        
        spread_percent = ((ask - bid) / bid) * 100
        
        # Select threshold based on setup type
        max_spread = (self.max_spread_percent_scalp if setup_type == 'scalp'
                     else self.max_spread_percent_swing)
        
        if spread_percent <= max_spread:
            return {
                'pass': True,
                'reason': f"{symbol}: Spread {spread_percent:.2f}% <= {max_spread}% threshold"
            }
        else:
            return {
                'pass': False,
                'reason': f"{symbol}: Spread {spread_percent:.2f}% > {max_spread}% threshold"
            }