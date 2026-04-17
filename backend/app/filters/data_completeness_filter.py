"""
Data Completeness Filter - Filter based on data availability
"""
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class DataCompletenessFilter:
    """
    Hard Filter: Data Completeness
    
    Rejects tickers with incomplete or missing data
    """
    
    def __init__(self):
        self.required_timeframes = ['15m', '1h', '4h', 'd']
    
    def filter(
        self,
        symbol: str,
        available_timeframes: Optional[list] = None,
        price_data_available: bool = True,
        volume_available: bool = True
    ) -> Dict:
        """
        Filter ticker based on data completeness
        
        Args:
            symbol: Ticker symbol
            available_timeframes: List of timeframes with data
            price_data_available: Whether price data is available
            volume_available: Whether volume data is available
            
        Returns:
            Dict with 'pass' status and reason
        """
        if not price_data_available:
            return {
                'pass': False,
                'reason': f"{symbol}: Price data not available"
            }
        
        if not volume_available:
            return {
                'pass': False,
                'reason': f"{symbol}: Volume data not available"
            }
        
        # Check if required timeframes are available
        if available_timeframes:
            missing = [tf for tf in self.required_timeframes if tf not in available_timeframes]
            if missing:
                return {
                    'pass': False,
                    'reason': f"{symbol}: Missing timeframes: {', '.join(missing)}"
                }
        
        return {
            'pass': True,
            'reason': f"{symbol}: All required data available"
        }