"""
ICT Engine - Rule-based structure detection
Deterministic, explainable technical analysis engine
"""
from typing import List, Dict, Optional
from ..models.ohlcv import OHLCVSeries
from ..models.analysis import ICTStructure, TrendBias
import logging

logger = logging.getLogger(__name__)


class ICTEngine:
    """
    ICT (Inner Circle Trader) Engine
    Detects trend, BOS/CHoCH, displacement, and liquidity sweeps
    """
    
    def __init__(self):
        # Minimum movement % for BOS/CHoCH conviction
        self.min_bos_movement = 0.2  # 0.2%
        
        # Minimum movement % for displacement
        self.min_displacement_15m = 1.5  # 1.5%
        self.min_displacement_1h = 2.0   # 2.0%
        
        # Momentum threshold for liquidity sweeps
        self.sweep_momentum_threshold = 0.5  # 0.5%
    
    def analyze(self, ohlcv_series: OHLCVSeries) -> ICTStructure:
        """
        Analyze OHLCV data using ICT methodology
        
        Args:
            ohlcv_series: OHLCV data for analysis
            
        Returns:
            ICTStructure with trend, BOS, displacement, and sweeps
        """
        if not ohlcv_series.candles:
            return ICTStructure(
                trend_bias=TrendBias.NEUTRAL,
                trend_confidence=0
            )
        
        # Detect trend
        trend_result = self._detect_trend(ohlcv_series)
        
        # Detect BOS/CHoCH
        bos_result = self._detect_bos_choch(ohlcv_series)
        
        # Detect displacement
        displacement = self._detect_displacement(ohlcv_series)
        
        # Detect liquidity sweeps
        sweeps = self._detect_liquidity_sweeps(ohlcv_series)
        
        return ICTStructure(
            trend_bias=trend_result['bias'],
            trend_confidence=trend_result['confidence'],
            bos_high=bos_result.get('bos_high'),
            bos_low=bos_result.get('bos_low'),
            most_recent_high=bos_result.get('most_recent_high'),
            most_recent_low=bos_result.get('most_recent_low'),
            displacement_detected=displacement['detected'],
            displacement_magnitude=displacement.get('magnitude'),
            liquidity_sweeps=sweeps
        )
    
    def _detect_trend(self, ohlcv_series: OHLCVSeries) -> Dict:
        """
        Detect trend using Higher Highs/Higher Lows or Lower Highs/Lower Lows
        
        Returns:
            Dict with bias and confidence (0-100)
        """
        closes = ohlcv_series.get_closes(10)
        highs = ohlcv_series.get_highs(10)
        lows = ohlcv_series.get_lows(10)
        
        if len(closes) < 3:
            return {'bias': TrendBias.NEUTRAL, 'confidence': 0}
        
        # Check for Higher Highs + Higher Lows (Bullish)
        recent_highs = highs[-3:]
        recent_lows = lows[-3:]
        
        hh_hl_count = 0
        lh_ll_count = 0
        
        # Count Higher Highs
        if recent_highs[1] > recent_highs[0] and recent_highs[2] > recent_highs[1]:
            hh_hl_count += 1
        
        # Count Higher Lows
        if recent_lows[1] > recent_lows[0] and recent_lows[2] > recent_lows[1]:
            hh_hl_count += 1
        
        # Count Lower Highs
        if recent_highs[1] < recent_highs[0] and recent_highs[2] < recent_highs[1]:
            lh_ll_count += 1
        
        # Count Lower Lows
        if recent_lows[1] < recent_lows[0] and recent_lows[2] < recent_lows[1]:
            lh_ll_count += 1
        
        # Determine bias
        if hh_hl_count >= 2:
            bias = TrendBias.BULLISH
            # Calculate magnitude based on price movement
            magnitude = (closes[-1] - closes[0]) / closes[0] * 100
            confidence = min(95, max(50, int(60 + magnitude * 10)))
        elif lh_ll_count >= 2:
            bias = TrendBias.BEARISH
            magnitude = (closes[0] - closes[-1]) / closes[0] * 100
            confidence = min(95, max(50, int(60 + magnitude * 10)))
        else:
            bias = TrendBias.NEUTRAL
            confidence = 50
        
        return {
            'bias': bias,
            'confidence': confidence
        }
    
    def _detect_bos_choch(self, ohlcv_series: OHLCVSeries) -> Dict:
        """
        Detect Break of Structure (BOS) or Change of Character (CHoCH)
        
        Returns:
            Dict with BOS levels and recent swing points
        """
        closes = ohlcv_series.get_closes(20)
        highs = ohlcv_series.get_highs(20)
        lows = ohlcv_series.get_lows(20)
        
        if len(closes) < 10:
            return {}
        
        # Find swing highs and lows (simplified approach)
        swing_highs = []
        swing_lows = []
        
        for i in range(2, len(highs) - 2):
            # Swing high: higher than neighbors
            if (highs[i] > highs[i-1] and highs[i] > highs[i-2] and
                highs[i] > highs[i+1] and highs[i] > highs[i+2]):
                swing_highs.append((i, highs[i]))
            
            # Swing low: lower than neighbors
            if (lows[i] < lows[i-1] and lows[i] < lows[i-2] and
                lows[i] < lows[i+1] and lows[i] < lows[i+2]):
                swing_lows.append((i, lows[i]))
        
        if not swing_highs or not swing_lows:
            return {
                'most_recent_high': highs[-1],
                'most_recent_low': lows[-1]
            }
        
        # Get most recent swing points
        most_recent_high_idx, most_recent_high = swing_highs[-1]
        most_recent_low_idx, most_recent_low = swing_lows[-1]
        
        # Check for BOS
        bos_high = None
        bos_low = None
        
        # Bullish BOS: close above recent swing high
        if closes[-1] > most_recent_high:
            movement = (closes[-1] - most_recent_high) / most_recent_high * 100
            if movement >= self.min_bos_movement:
                bos_high = closes[-1]
        
        # Bearish BOS: close below recent swing low
        if closes[-1] < most_recent_low:
            movement = (most_recent_low - closes[-1]) / most_recent_low * 100
            if movement >= self.min_bos_movement:
                bos_low = closes[-1]
        
        return {
            'bos_high': bos_high,
            'bos_low': bos_low,
            'most_recent_high': most_recent_high,
            'most_recent_low': most_recent_low
        }
    
    def _detect_displacement(self, ohlcv_series: OHLCVSeries) -> Dict:
        """
        Detect impulsive displacement moves
        
        Returns:
            Dict with detection status and magnitude
        """
        timeframe = ohlcv_series.timeframe
        closes = ohlcv_series.get_closes(5)
        
        if len(closes) < 3:
            return {'detected': False}
        
        # Determine minimum movement based on timeframe
        if timeframe in ['1m', '5m', '15m']:
            min_movement = self.min_displacement_15m
        else:
            min_movement = self.min_displacement_1h
        
        # Check for impulsive move (strong candles in same direction)
        movement = abs(closes[-1] - closes[-3]) / closes[-3] * 100
        
        if movement >= min_movement:
            return {
                'detected': True,
                'magnitude': movement,
                'type': 'bullish' if closes[-1] > closes[-3] else 'bearish'
            }
        
        return {'detected': False}
    
    def _detect_liquidity_sweeps(self, ohlcv_series: OHLCVSeries) -> List[Dict]:
        """
        Detect liquidity sweeps at swing highs/lows
        
        Returns:
            List of detected sweeps
        """
        sweeps = []
        
        highs = ohlcv_series.get_highs(20)
        lows = ohlcv_series.get_lows(20)
        closes = ohlcv_series.get_closes(20)
        
        if len(closes) < 5:
            return sweeps
        
        # Look for rapid rejection of swing points
        for i in range(3, len(closes) - 1):
            # Check for sweep at swing high
            if highs[i] == max(highs[max(0, i-2):i+3]):
                # Price tested high and then rejected
                if (closes[i] < highs[i] and closes[i+1] < closes[i] and
                    abs(closes[i] - closes[i+1]) / closes[i] * 100 >= self.sweep_momentum_threshold):
                    sweeps.append({
                        'type': 'bearish_sweep',
                        'level': highs[i],
                        'timestamp': ohlcv_series.candles[i].timestamp,
                        'strength': 'moderate' if abs(closes[i] - closes[i+1]) / closes[i] * 100 >= 0.8 else 'weak'
                    })
            
            # Check for sweep at swing low
            if lows[i] == min(lows[max(0, i-2):i+3]):
                # Price tested low and then rejected
                if (closes[i] > lows[i] and closes[i+1] > closes[i] and
                    abs(closes[i] - closes[i+1]) / closes[i] * 100 >= self.sweep_momentum_threshold):
                    sweeps.append({
                        'type': 'bullish_sweep',
                        'level': lows[i],
                        'timestamp': ohlcv_series.candles[i].timestamp,
                        'strength': 'moderate' if abs(closes[i] - closes[i+1]) / closes[i] * 100 >= 0.8 else 'weak'
                    })
        
        return sweeps