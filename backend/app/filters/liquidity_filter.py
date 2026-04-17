"""
Liquidity Filter - Filter based on options liquidity grade
"""
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class LiquidityFilter:
    """
    Hard Filter: Options Liquidity
    
    Rejects tickers with insufficient options liquidity
    Only allows Grade A or Grade B options
    """
    
    def __init__(self):
        self.min_liquidity_grade = 'B'  # Accept Grade B and above
    
    def filter(
        self,
        symbol: str,
        volume: Optional[int] = None,
        open_interest: Optional[int] = None
    ) -> Dict:
        """
        Filter ticker based on options liquidity
        
        Args:
            symbol: Ticker symbol
            volume: Option volume
            open_interest: Option open interest
            
        Returns:
            Dict with 'pass' status and reason
        """
        if volume is None or open_interest is None:
            return {
                'pass': False,
                'reason': f"{symbol}: Liquidity data not available"
            }
        
        # Calculate liquidity grade
        grade = self._calculate_liquidity_grade(volume, open_interest)
        
        if grade == 'A':
            return {
                'pass': True,
                'reason': f"{symbol}: Grade A liquidity (Volume: {volume:,}, OI: {open_interest:,})"
            }
        elif grade == 'B':
            return {
                'pass': True,
                'reason': f"{symbol}: Grade B liquidity (Volume: {volume:,}, OI: {open_interest:,})"
            }
        else:
            return {
                'pass': False,
                'reason': f"{symbol}: Grade {grade} liquidity - below minimum {self.min_liquidity_grade}"
            }
    
    def _calculate_liquidity_grade(self, volume: int, open_interest: int) -> str:
        """
        Calculate liquidity grade based on volume and open interest
        
        Grade A: Volume ≥ 10,000 AND Open Interest ≥ 5,000 AND Spread < 2%
        Grade B: Volume ≥ 5,000 AND Open Interest ≥ 2,000 AND Spread < 5%
        Grade C: Volume ≥ 1,000 AND Open Interest ≥ 500 AND Spread < 10%
        Grade D: Below Grade C
        """
        if (volume >= 10000 and open_interest >= 5000):
            return 'A'
        elif (volume >= 5000 and open_interest >= 2000):
            return 'B'
        elif (volume >= 1000 and open_interest >= 500):
            return 'C'
        else:
            return 'D'