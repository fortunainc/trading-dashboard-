"""
Analysis result models
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum


class TrendBias(str, Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class SetupType(str, Enum):
    BULLISH_CONTINUATION = "bullish_continuation"
    BEARISH_CONTINUATION = "bearish_continuation"
    BULLISH_REVERSAL = "bullish_reversal"
    BEARISH_REVERSAL = "bearish_reversal"
    NONE = "none"


@dataclass
class ICTStructure:
    """ICT structure analysis result"""
    trend_bias: TrendBias
    trend_confidence: int  # 0-100
    bos_high: Optional[float] = None
    bos_low: Optional[float] = None
    most_recent_high: Optional[float] = None
    most_recent_low: Optional[float] = None
    displacement_detected: bool = False
    displacement_magnitude: Optional[float] = None
    liquidity_sweeps: List[Dict] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            'trend_bias': self.trend_bias.value,
            'trend_confidence': self.trend_confidence,
            'bos_high': self.bos_high,
            'bos_low': self.bos_low,
            'most_recent_high': self.most_recent_high,
            'most_recent_low': self.most_recent_low,
            'displacement_detected': self.displacement_detected,
            'displacement_magnitude': self.displacement_magnitude,
            'liquidity_sweeps': self.liquidity_sweeps
        }


@dataclass
class STRATCandle:
    """STRAT candle classification"""
    candle_index: int
    timestamp: datetime
    candle_type: str  # '1', '2U', '2D', '3'
    body_percent: float
    upper_wick_percent: float
    lower_wick_percent: float
    
    def to_dict(self) -> dict:
        return {
            'candle_index': self.candle_index,
            'timestamp': self.timestamp,
            'candle_type': self.candle_type,
            'body_percent': self.body_percent,
            'upper_wick_percent': self.upper_wick_percent,
            'lower_wick_percent': self.lower_wick_percent
        }


@dataclass
class STRATAnalysis:
    """STRAT analysis result"""
    bias: TrendBias
    confidence: int  # 0-100
    candles: List[STRATCandle]
    pattern_sequence: str
    conflict_detected: bool = False
    conflict_details: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            'bias': self.bias.value,
            'confidence': self.confidence,
            'candles': [c.to_dict() for c in self.candles],
            'pattern_sequence': self.pattern_sequence,
            'conflict_detected': self.conflict_detected,
            'conflict_details': self.conflict_details
        }


@dataclass
class FVG:
    """Fair Value Gap"""
    fvg_type: str  # 'bullish', 'bearish'
    high: float
    low: float
    gap_percent: float
    created_at: datetime
    tested: bool = False
    test_count: int = 0
    
    def to_dict(self) -> dict:
        return {
            'type': self.fvg_type,
            'high': self.high,
            'low': self.low,
            'gap_percent': self.gap_percent,
            'created_at': self.created_at,
            'tested': self.tested,
            'test_count': self.test_count
        }


@dataclass
class FVGAnalysis:
    """FVG analysis result"""
    fresh_fvgs: List[FVG] = field(default_factory=list)
    ageing_fvgs: List[FVG] = field(default_factory=list)
    stale_fvgs: List[FVG] = field(default_factory=list)
    untested_fvgs: List[FVG] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            'fresh_fvgs': [f.to_dict() for f in self.fresh_fvgs],
            'ageing_fvgs': [f.to_dict() for f in self.ageing_fvgs],
            'stale_fvgs': [f.to_dict() for f in self.stale_fvgs],
            'untested_fvgs': [f.to_dict() for f in self.untested_fvgs]
        }


@dataclass
class Scoring:
    """Scoring result with explainable components"""
    scalp_score: int  # 0-100
    swing_score: int  # 0-100
    structure_quality: str  # 'A', 'B', 'C'
    confluence_level: str  # 'weak', 'moderate', 'strong'
    
    # Scalp score components
    scalp_ict_structure: int = 0
    scalp_strat_alignment: int = 0
    scalp_fvg_freshness: int = 0
    scalp_confluence: int = 0
    
    # Swing score components
    swing_ict_structure: int = 0
    swing_strat_alignment: int = 0
    swing_fvg_freshness: int = 0
    swing_confluence: int = 0
    
    def to_dict(self) -> dict:
        return {
            'scalp_score': self.scalp_score,
            'scalp_ict_structure': self.scalp_ict_structure,
            'scalp_strat_alignment': self.scalp_strat_alignment,
            'scalp_fvg_freshness': self.scalp_fvg_freshness,
            'scalp_confluence': self.scalp_confluence,
            'swing_score': self.swing_score,
            'swing_ict_structure': self.swing_ict_structure,
            'swing_strat_alignment': self.swing_strat_alignment,
            'swing_fvg_freshness': self.swing_fvg_freshness,
            'swing_confluence': self.swing_confluence,
            'structure_quality': self.structure_quality,
            'confluence_level': self.confluence_level
        }


@dataclass
class Contract:
    """Option contract suggestion"""
    rank: int
    contract: str
    dte: int
    delta: float
    bid: float
    ask: float
    spread_percent: float
    volume: int
    open_interest: int
    iv: float
    liquidity_grade: str
    rationale: str
    entry_limit: float
    target: float
    stop_loss: float
    
    def to_dict(self) -> dict:
        return {
            'rank': self.rank,
            'contract': self.contract,
            'dte': self.dte,
            'delta': self.delta,
            'bid': self.bid,
            'ask': self.ask,
            'spread_percent': self.spread_percent,
            'volume': self.volume,
            'open_interest': self.open_interest,
            'iv': self.iv,
            'liquidity_grade': self.liquidity_grade,
            'rationale': self.rationale,
            'entry_limit': self.entry_limit,
            'target': self.target,
            'stop_loss': self.stop_loss
        }


@dataclass
class CompleteAnalysis:
    """Complete analysis result for a ticker"""
    symbol: str
    timestamp: datetime
    official_close: float
    
    # Engine outputs
    ict_structure: ICTStructure
    strat_analysis: STRATAnalysis
    fvg_analysis: FVGAnalysis
    
    # Filter results
    hard_filter_passed: bool
    filter_reasons: List[str] = field(default_factory=list)
    
    # Scoring
    scoring: Optional[Scoring] = None
    
    # Setup identification
    setup_type: SetupType = SetupType.NONE
    
    # Contracts
    scalp_contracts: List[Contract] = field(default_factory=list)
    swing_contracts: List[Contract] = field(default_factory=list)
    
    # Thesis
    prep_thesis: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            'symbol': self.symbol,
            'timestamp': self.timestamp,
            'official_close': self.official_close,
            'ict_structure': self.ict_structure.to_dict(),
            'strat_analysis': self.strat_analysis.to_dict(),
            'fvg_analysis': self.fvg_analysis.to_dict(),
            'hard_filter_passed': self.hard_filter_passed,
            'filter_reasons': self.filter_reasons,
            'scoring': self.scoring.to_dict() if self.scoring else None,
            'setup_type': self.setup_type.value,
            'scalp_contracts': [c.to_dict() for c in self.scalp_contracts],
            'swing_contracts': [c.to_dict() for c in self.swing_contracts],
            'prep_thesis': self.prep_thesis
        }