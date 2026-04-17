"""
Market Regime Filter - Filter based on overall market regime
"""
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class MarketRegimeFilter:
    """
    Hard Filter: Market Regime
    
    Rejects tickers in unfavorable market regimes
    """
    
    def __init__(self):
        self.bad_regimes = ['bear_crash', 'extreme_volatility', 'closed']
    
    def filter(
        self,
        symbol: str,
        market_regime: str,
        spy_change_percent: Optional[float] = None,
        vix: Optional[float] = None
    ) -> Dict:
        """
        Filter ticker based on market regime
        
        Args:
            symbol: Ticker symbol
            market_regime: Current market regime
            spy_change_percent: SPY percent change
            vix: VIX level
            
        Returns:
            Dict with 'pass' status and reason
        """
        # Check if regime is explicitly bad
        if market_regime in self.bad_regimes:
            return {
                'pass': False,
                'reason': f"{symbol}: Market regime '{market_regime}' is unfavorable for trading"
            }
        
        # Check for bear crash (SPY gap down > 2%)
        if spy_change_percent is not None and spy_change_percent < -2.0:
            return {
                'pass': False,
                'reason': f"{symbol}: Bear crash detected - SPY down {abs(spy_change_percent):.2f}%"
            }
        
        # Check for extreme volatility (VIX > 35)
        if vix is not None and vix > 35:
            return {
                'pass': False,
                'reason': f"{symbol}: Extreme volatility detected - VIX at {vix:.1f}"
            }
        
        return {
            'pass': True,
            'reason': f"{symbol}: Market regime '{market_regime}' is acceptable"
        }