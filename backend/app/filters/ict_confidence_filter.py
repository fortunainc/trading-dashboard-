"""
ICT Confidence Filter - Filter based on ICT engine confidence
"""
from typing import Dict
from ..models.analysis import ICTStructure
import logging

logger = logging.getLogger(__name__)


class ICTConfidenceFilter:
    """
    Hard Filter: ICT Confidence
    
    Rejects tickers with low ICT confidence scores
    """
    
    def __init__(self):
        self.min_ict_confidence = 60  # Minimum 60/100
    
    def filter(self, symbol: str, ict_structure: ICTStructure) -> Dict:
        """
        Filter ticker based on ICT confidence
        
        Args:
            symbol: Ticker symbol
            ict_structure: ICT structure analysis result
            
        Returns:
            Dict with 'pass' status and reason
        """
        confidence = ict_structure.trend_confidence
        
        if confidence >= self.min_ict_confidence:
            return {
                'pass': True,
                'reason': f"{symbol}: ICT confidence {confidence}/100 >= {self.min_ict_confidence}"
            }
        else:
            return {
                'pass': False,
                'reason': f"{symbol}: ICT confidence {confidence}/100 < {self.min_ict_confidence}"
            }