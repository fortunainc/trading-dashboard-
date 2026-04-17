"""
Structure Freshness Filter - Filter based on structure recency
"""
from typing import Dict
from datetime import datetime, timedelta
from ..models.analysis import ICTStructure
import logging

logger = logging.getLogger(__name__)


class StructureFreshnessFilter:
    """
    Hard Filter: Structure Freshness
    
    Rejects tickers with stale structure analysis
    Structure should be recent (within last few hours for intraday)
    """
    
    def __init__(self):
        self.max_age_hours = 8  # Structure must be within 8 hours (one trading day)
    
    def filter(
        self,
        symbol: str,
        structure_timestamp: datetime,
        current_time: datetime = None
    ) -> Dict:
        """
        Filter ticker based on structure freshness
        
        Args:
            symbol: Ticker symbol
            structure_timestamp: When structure was last analyzed
            current_time: Current time (defaults to now)
            
        Returns:
            Dict with 'pass' status and reason
        """
        if current_time is None:
            current_time = datetime.now()
        
        age = current_time - structure_timestamp
        age_hours = age.total_seconds() / 3600
        
        if age_hours <= self.max_age_hours:
            return {
                'pass': True,
                'reason': f"{symbol}: Structure is {age_hours:.1f} hours old (fresh)"
            }
        else:
            return {
                'pass': False,
                'reason': f"{symbol}: Structure is {age_hours:.1f} hours old (stale, max {self.max_age_hours}h)"
            }