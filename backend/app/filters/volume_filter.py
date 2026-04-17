"""
Volume Filter - Filter based on trading volume
"""
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class VolumeFilter:
    """
    Hard Filter: Volume
    
    Rejects tickers with insufficient trading volume
    """
    
    def __init__(self):
        self.min_volume_ratio = 0.5  # Minimum 50% of average volume
        self.min_absolute_volume = 500000  # Minimum 500K shares absolute
    
    def filter(
        self,
        symbol: str,
        current_volume: Optional[int] = None,
        average_volume: Optional[int] = None
    ) -> Dict:
        """
        Filter ticker based on volume
        
        Args:
            symbol: Ticker symbol
            current_volume: Current trading volume
            average_volume: Average daily volume
            
        Returns:
            Dict with 'pass' status and reason
        """
        if current_volume is None:
            return {
                'pass': False,
                'reason': f"{symbol}: Volume data not available"
            }
        
        # Check absolute minimum
        if current_volume < self.min_absolute_volume:
            return {
                'pass': False,
                'reason': f"{symbol}: Volume {current_volume:,} < minimum {self.min_absolute_volume:,}"
            }
        
        # Check relative to average if available
        if average_volume is not None and average_volume > 0:
            volume_ratio = current_volume / average_volume
            
            if volume_ratio < self.min_volume_ratio:
                return {
                    'pass': False,
                    'reason': f"{symbol}: Volume is {volume_ratio:.1%} of average (min {self.min_volume_ratio:.0%})"
                }
        
        return {
            'pass': True,
            'reason': f"{symbol}: Volume is acceptable"
        }