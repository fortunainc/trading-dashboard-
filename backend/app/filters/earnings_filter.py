"""
Earnings Filter - Filter tickers with upcoming earnings
"""
from typing import Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class EarningsFilter:
    """
    Hard Filter: Earnings Stand-Down
    
    Rejects tickers with earnings within the stand-down window
    """
    
    def __init__(self):
        self.stand_down_days = 7  # 7 days before earnings
    
    def filter(
        self,
        symbol: str,
        earnings_date: Optional[datetime] = None,
        current_date: Optional[datetime] = None
    ) -> Dict:
        """
        Filter ticker based on upcoming earnings
        
        Args:
            symbol: Ticker symbol
            earnings_date: Next earnings date
            current_date: Current date (defaults to today)
            
        Returns:
            Dict with 'pass' status and reason
        """
        if earnings_date is None:
            # No earnings date available, assume no upcoming earnings
            return {
                'pass': True,
                'reason': f"{symbol}: No upcoming earnings data, passing filter"
            }
        
        if current_date is None:
            current_date = datetime.now()
        
        days_to_earnings = (earnings_date - current_date).days
        
        # If earnings is within stand-down window
        if 0 <= days_to_earnings <= self.stand_down_days:
            return {
                'pass': False,
                'reason': f"{symbol}: Earnings in {days_to_earnings} days - stand-down window (max {self.stand_down_days}d)"
            }
        
        # If earnings already passed (negative days), check if very recent
        if days_to_earnings < 0 and abs(days_to_earnings) <= 2:
            return {
                'pass': False,
                'reason': f"{symbol}: Earnings occurred {abs(days_to_earnings)} days ago - volatility too high"
            }
        
        return {
            'pass': True,
            'reason': f"{symbol}: Earnings in {days_to_earnings} days - outside stand-down window"
        }