"""
STRAT Freshness Filter - Filter based on STRAT data freshness
"""
from typing import Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class STRATFreshnessFilter:
    """
    Hard Filter: STRAT Freshness
    
    Rejects tickers with stale STRAT data
    STRAT analysis should be from the current trading day
    """
    
    def __init__(self):
        self.max_age_hours = 24  # STRAT data must be within 24 hours
    
    def filter(
        self,
        symbol: str,
        analysis_timestamp: datetime,
        current_time: datetime = None
    ) -> Dict:
        """
        Filter ticker based on STRAT data freshness
        
        Args:
            symbol: Ticker symbol
            analysis_timestamp: When the STRAT analysis was performed
            current_time: Current time (defaults to now)
            
        Returns:
            Dict with 'pass' status and reason
        """
        if current_time is None:
            current_time = datetime.now()
        
        age = current_time - analysis_timestamp
        age_hours = age.total_seconds() / 3600
        
        if age_hours <= self.max_age_hours:
            return {
                'pass': True,
                'reason': f"{symbol}: STRAT analysis is {age_hours:.1f} hours old (fresh)"
            }
        else:
            return {
                'pass': False,
                'reason': f"{symbol}: STRAT analysis is {age_hours:.1f} hours old (stale, max {self.max_age_hours}h)"
            }