"""
STRAT Engine - Multi-timeframe candle classification
Deterministic, rule-based candle pattern analysis
"""
from typing import List, Dict, Optional
from datetime import datetime
from ..models.ohlcv import OHLCVSeries, OHLCVCandle
from ..models.analysis import STRATAnalysis, STRATCandle, TrendBias
import logging

logger = logging.getLogger(__name__)


class STRATEngine:
    """
    STRAT Engine (Smart Risk Reward And Trading)
    Classifies candles as Type 1, 2U, 2D, or Type 3
    """
    
    def __init__(self):
        # Candle classification thresholds (deterministic)
        self.continuation_body_threshold = 0.6  # 60% of range
        self.rejection_wick_threshold = 0.4     # 40% of range
        self.balance_body_threshold = 0.3       # 30% of range
        self.type3_body_threshold = 0.4         # 40% for Type 3
    
    def analyze(self, ohlcv_series: OHLCVSeries, num_candles: int = 10) -> STRATAnalysis:
        """
        Analyze candles using STRAT methodology
        
        Args:
            ohlcv_series: OHLCV data
            num_candles: Number of recent candles to analyze
            
        Returns:
            STRATAnalysis with candle classifications and pattern
        """
        if not ohlcv_series.candles:
            return STRATAnalysis(
                bias=TrendBias.NEUTRAL,
                confidence=0,
                candles=[],
                pattern_sequence=""
            )
        
        # Get recent candles
        recent_candles = ohlcv_series.get_candles_count(num_candles)
        
        # Calculate average body and range for context
        avg_body, avg_range = self._calculate_averages(recent_candles)
        
        # Classify each candle
        classified_candles = []
        pattern_sequence = ""
        
        for i, candle in enumerate(recent_candles):
            classification = self._classify_candle(candle, avg_body, avg_range)
            classified_candles.append(classification)
            pattern_sequence += classification['type']
        
        # Determine bias from pattern
        bias, confidence = self._determine_bias(classified_candles)
        
        # Check for conflicts
        conflict_detected, conflict_details = self._check_conflicts(classified_candles)
        
        return STRATAnalysis(
            bias=bias,
            confidence=confidence,
            classified_candles=classified_candles,
            pattern_sequence=pattern_sequence,
            conflict_detected=conflict_detected,
            conflict_details=conflict_details
        )
    
    def _calculate_averages(self, candles: List[OHLCVCandle]) -> tuple:
        """Calculate average body and range"""
        bodies = []
        ranges_list = []
        
        for candle in candles:
            body = abs(candle.close - candle.open)
            range_val = candle.high - candle.low
            bodies.append(body)
            ranges_list.append(range_val)
        
        avg_body = sum(bodies) / len(bodies) if bodies else 0
        avg_range = sum(ranges_list) / len(ranges_list) if ranges_list else 0
        
        return avg_body, avg_range
    
    def _classify_candle(self, candle: OHLCVCandle, avg_body: float, avg_range: float) -> Dict:
        """
        Classify candle as Type 1, 2U, 2D, or Type 3
        
        Classification rules:
        - Type 1: Continuation candle (strong body in direction of close)
        - Type 2U: Rejection of highs (long upper wick, bearish close)
        - Type 2D: Rejection of lows (long lower wick, bullish close)
        - Type 3: Balanced candle (indcision)
        """
        body_size = abs(candle.close - candle.open)
        range_size = candle.high - candle.low
        
        if range_size == 0:
            return {
                'type': '3',
                'body_percent': 0,
                'upper_wick_percent': 0,
                'lower_wick_percent': 0,
                'classification': 'Type 3 (Indcision)'
            }
        
        # Calculate percentages
        body_percent = (body_size / range_size) * 100
        upper_wick = (candle.high - max(candle.open, candle.close))
        lower_wick = (min(candle.open, candle.close) - candle.low)
        upper_wick_percent = (upper_wick / range_size) * 100
        lower_wick_percent = (lower_wick / range_size) * 100
        
        is_bullish = candle.close > candle.open
        
        # Type 1: Continuation candle
        # Strong body (>= 60% of range) in direction of close
        if body_percent >= self.continuation_body_threshold:
            if is_bullish:
                # Bullish continuation: close at or near top of range
                if lower_wick_percent <= (100 - body_percent) * 0.5:
                    candle_type = '1'
                    classification = 'Type 1 (Bullish Continuation)'
                else:
                    candle_type = '3'
                    classification = 'Type 3 (Indcision)'
            else:
                # Bearish continuation: close at or near bottom of range
                if upper_wick_percent <= (100 - body_percent) * 0.5:
                    candle_type = '1'
                    classification = 'Type 1 (Bearish Continuation)'
                else:
                    candle_type = '3'
                    classification = 'Type 3 (Indcision)'
        
        # Type 2U: Rejection of highs
        elif (upper_wick_percent >= self.rejection_wick_threshold and
              body_percent >= self.balance_body_threshold and
              not is_bullish):
            candle_type = '2U'
            classification = 'Type 2U (Rejection of Highs)'
        
        # Type 2D: Rejection of lows
        elif (lower_wick_percent >= self.rejection_wick_threshold and
              body_percent >= self.balance_body_threshold and
              is_bullish):
            candle_type = '2D'
            classification = 'Type 2D (Rejection of Lows)'
        
        # Type 3: Indcision / Balanced
        else:
            candle_type = '3'
            classification = 'Type 3 (Indcision)'
        
        return {
            'type': candle_type,
            'body_percent': round(body_percent, 1),
            'upper_wick_percent': round(upper_wick_percent, 1),
            'lower_wick_percent': round(lower_wick_percent, 1),
            'classification': classification,
            'is_bullish': is_bullish
        }
    
    def _determine_bias(self, classified_candles: List[Dict]) -> tuple:
        """
        Determine bias from candle sequence
        
        Returns:
            Tuple of (TrendBias, confidence 0-100)
        """
        if not classified_candles:
            return TrendBias.NEUTRAL, 0
        
        bullish_candles = sum(1 for c in classified_candles if c.get('is_bullish'))
        bearish_candles = sum(1 for c in classified_candles if not c.get('is_bullish'))
        total = len(classified_candles)
        
        # Count continuation vs reversal candles
        type1_bullish = sum(1 for c in classified_candles if c['type'] == '1' and c.get('is_bullish'))
        type1_bearish = sum(1 for c in classified_candles if c['type'] == '1' and not c.get('is_bullish'))
        
        # Determine bias based on Type 1 candles (strongest signal)
        if type1_bullish > type1_bearish:
            bias = TrendBias.BULLISH
            confidence = min(95, int(50 + (type1_bullish / total) * 50))
        elif type1_bearish > type1_bullish:
            bias = TrendBias.BEARISH
            confidence = min(95, int(50 + (type1_bearish / total) * 50))
        else:
            # If equal, look at overall bias
            if bullish_candles > bearish_candles:
                bias = TrendBias.BULLISH
                confidence = int((bullish_candles / total) * 80)
            elif bearish_candles > bullish_candles:
                bias = TrendBias.BEARISH
                confidence = int((bearish_candles / total) * 80)
            else:
                bias = TrendBias.NEUTRAL
                confidence = 50
        
        return bias, confidence
    
    def _check_conflicts(self, classified_candles: List[Dict]) -> tuple:
        """
        Check for conflicts in candle pattern
        
        Returns:
            Tuple of (conflict_detected: bool, conflict_details: str)
        """
        if len(classified_candles) < 3:
            return False, None
        
        # Check for mixed signals in recent candles
        recent = classified_candles[-3:]
        bullish_count = sum(1 for c in recent if c.get('is_bullish'))
        bearish_count = sum(1 for c in recent if not c.get('is_bullish'))
        
        # If we have both strong bullish and bearish signals
        type1_bullish = sum(1 for c in recent if c['type'] == '1' and c.get('is_bullish'))
        type1_bearish = sum(1 for c in recent if c['type'] == '1' and not c.get('is_bullish'))
        
        if type1_bullish > 0 and type1_bearish > 0:
            return True, "Mixed Type 1 candles in recent pattern - directional conflict"
        
        # Check for chop (too many Type 2 and 3 candles)
        type2_count = sum(1 for c in recent if c['type'] in ['2U', '2D'])
        type3_count = sum(1 for c in recent if c['type'] == '3')
        
        if type2_count >= 2 or type3_count >= 2:
            return True, f"Choppy pattern detected: {type2_count} Type 2, {type3_count} Type 3 candles"
        
        return False, None