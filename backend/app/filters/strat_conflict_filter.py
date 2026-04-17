"""
STRAT Conflict Filter - Filter tickers with STRAT conflict
"""
from typing import Dict
from ..models.analysis import STRATAnalysis
import logging

logger = logging.getLogger(__name__)


class STRATConflictFilter:
    """
    Hard Filter: STRAT Conflict
    
    Rejects tickers with conflicting STRAT signals
    """
    
    def __init__(self):
        pass
    
    def filter(self, symbol: str, strat_analysis: STRATAnalysis) -> Dict:
        """
        Filter ticker based on STRAT conflict
        
        Args:
            symbol: Ticker symbol
            strat_analysis: STRAT analysis result
            
        Returns:
            Dict with 'pass' status and reason
        """
        if strat_analysis.conflict_detected:
            return {
                'pass': False,
                'reason': f"{symbol}: STRAT conflict detected - {strat_analysis.conflict_details}"
            }
        else:
            return {
                'pass': True,
                'reason': f"{symbol}: No STRAT conflict"
            }