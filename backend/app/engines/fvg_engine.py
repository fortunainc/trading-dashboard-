"""
FVG Engine - Fair Value Gap detection
Deterministic gap detection with freshness tracking
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from ..models.ohlcv import OHLCVSeries
from ..models.analysis import FVGAnalysis, FVG
import logging

logger = logging.getLogger(__name__)


class FVGEngine:
    """
    Fair Value Gap (FVG) Engine
    Detects fair value gaps and tracks freshness
    """
    
    def __init__(self):
        # Freshness thresholds (in days)
        self.fresh_threshold_days = 1
        self.ageing_threshold_days = 3
        
        # Minimum gap size percentage
        self.min_gap_percent = 0.05  # 0.05%
    
    def analyze(self, ohlcv_series: OHLCVSeries) -> FVGAnalysis:
        """
        Analyze OHLCV data for Fair Value Gaps
        
        Args:
            ohlcv_series: OHLCV data
            
        Returns:
            FVGAnalysis with detected gaps categorized by freshness
        """
        if not ohlcv_series.candles or len(ohlcv_series.candles) < 3:
            return FVGAnalysis()
        
        # Detect all FVGs
        all_fvgs = self._detect_fvgs(ohlcv_series)
        
        # Update test status based on current price
        current_price = ohlcv_series.get_latest_candle().close if ohlcv_series.get_latest_candle() else None
        if current_price:
            all_fvgs = self._update_test_status(all_fvgs, current_price)
        
        # Categorize by freshness
        fresh_fvgs = []
        ageing_fvgs = []
        stale_fvgs = []
        untested_fvgs = []
        
        now = datetime.now()
        
        for fvg in all_fvgs:
            age_days = (now - fvg.created_at).days
            
            if age_days < self.fresh_threshold_days:
                fresh_fvgs.append(fvg)
            elif age_days < self.ageing_threshold_days:
                ageing_fvgs.append(fvg)
            else:
                stale_fvgs.append(fvg)
            
            if not fvg.tested:
                untested_fvgs.append(fvg)
        
        return FVGAnalysis(
            fresh_fvgs=fresh_fvgs,
            ageing_fvgs=ageing_fvgs,
            stale_fvgs=stale_fvgs,
            untested_fvgs=untested_fvgs
        )
    
    def _detect_fvgs(self, ohlcv_series: OHLCVSeries) -> List[FVG]:
        """
        Detect Fair Value Gaps in the candle series
        
        Bullish FVG: candle3 low > candle1 high (gap to the upside)
        Bearish FVG: candle3 high < candle1 low (gap to the downside)
        
        Args:
            ohlcv_series: OHLCV data
            
        Returns:
            List of detected FVGs
        """
        candles = ohlcv_series.candles
        fvgs = []
        
        if len(candles) < 3:
            return fvgs
        
        for i in range(2, len(candles)):
            candle1 = candles[i - 2]
            candle2 = candles[i - 1]
            candle3 = candles[i]
            
            # Check for Bullish FVG
            if candle3.low > candle1.high:
                gap_size = candle3.low - candle1.high
                gap_percent = (gap_size / candle1.high) * 100
                
                if gap_percent >= self.min_gap_percent:
                    fvg = FVG(
                        fvg_type='bullish',
                        high=candle3.low,
                        low=candle1.high,
                        gap_percent=round(gap_percent, 3),
                        created_at=candle3.timestamp,
                        tested=False,
                        test_count=0
                    )
                    fvgs.append(fvg)
            
            # Check for Bearish FVG
            elif candle3.high < candle1.low:
                gap_size = candle1.low - candle3.high
                gap_percent = (gap_size / candle1.low) * 100
                
                if gap_percent >= self.min_gap_percent:
                    fvg = FVG(
                        fvg_type='bearish',
                        high=candle1.low,
                        low=candle3.high,
                        gap_percent=round(gap_percent, 3),
                        created_at=candle3.timestamp,
                        tested=False,
                        test_count=0
                    )
                    fvgs.append(fvg)
        
        return fvgs
    
    def _update_test_status(self, fvgs: List[FVG], current_price: float) -> List[FVG]:
        """
        Update test status of FVGs based on current price
        
        An FVG is "tested" if price trades into the gap zone
        
        Args:
            fvgs: List of FVGs
            current_price: Current price
            
        Returns:
            Updated list of FVGs
        """
        for fvg in fvgs:
            if fvg.fvg_type == 'bullish':
                # Bullish FVG is tested if price trades into the gap zone
                if fvg.low <= current_price <= fvg.high:
                    if not fvg.tested:
                        fvg.tested = True
                    fvg.test_count += 1
            
            elif fvg.fvg_type == 'bearish':
                # Bearish FVG is tested if price trades into the gap zone
                if fvg.low <= current_price <= fvg.high:
                    if not fvg.tested:
                        fvg.tested = True
                    fvg.test_count += 1
        
        return fvgs
    
    def get_key_support_resistance(self, fvgs: List[FVG], fvg_type: str = 'bullish') -> Dict:
        """
        Get key support or resistance levels from FVGs
        
        Args:
            fvgs: List of FVGs
            fvg_type: 'bullish' for support, 'bearish' for resistance
            
        Returns:
            Dict with key levels
        """
        filtered_fvgs = [f for f in fvgs if f.fvg_type == fvg_type]
        
        if not filtered_fvgs:
            return {
                'primary': None,
                'secondary': None,
                'count': 0
            }
        
        # Sort by creation time (most recent first)
        sorted_fvgs = sorted(filtered_fvgs, key=lambda x: x.created_at, reverse=True)
        
        # Primary: most recent untested FVG
        primary = None
        secondary = None
        
        for fvg in sorted_fvgs:
            if not fvg.tested:
                if primary is None:
                    primary = fvg
                elif secondary is None:
                    secondary = fvg
                    break
        
        return {
            'primary': primary.to_dict() if primary else None,
            'secondary': secondary.to_dict() if secondary else None,
            'count': len(filtered_fvgs)
        }