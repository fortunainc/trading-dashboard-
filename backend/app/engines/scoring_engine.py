"""
Scoring Engine - Explainable scoring with component breakdown
Deterministic scoring based on engine outputs and confluence
"""
from typing import Dict, Optional
from ..models.analysis import (
    ICTStructure, STRATAnalysis, FVGAnalysis, Scoring,
    SetupType, TrendBias
)
import logging

logger = logging.getLogger(__name__)


class ScoringEngine:
    """
    Scoring Engine
    Generates explainable scores for scalp and swing setups
    """
    
    def __init__(self):
        # Weight distributions (must sum to 100 for each score type)
        self.scalp_weights = {
            'ict_structure': 30,
            'strat_alignment': 30,
            'fvg_freshness': 20,
            'confluence': 20
        }
        
        self.swing_weights = {
            'ict_structure': 25,
            'strat_alignment': 25,
            'fvg_freshness': 25,
            'confluence': 25
        }
        
        # Confidence thresholds
        self.high_confidence_threshold = 80
        self.medium_confidence_threshold = 60
    
    def calculate_scores(
        self,
        ict_structure: ICTStructure,
        strat_analysis: STRATAnalysis,
        fvg_analysis: FVGAnalysis
    ) -> Scoring:
        """
        Calculate scores for scalp and swing setups
        
        Args:
            ict_structure: ICT engine output
            strat_analysis: STRAT engine output
            fvg_analysis: FVG engine output
            
        Returns:
            Scoring object with scalp and swing scores
        """
        # Calculate component scores
        ict_score = self._score_ict_structure(ict_structure)
        strat_score = self._score_strat_alignment(strat_analysis)
        fvg_score = self._score_fvg_freshness(fvg_analysis)
        confluence_score = self._calculate_confluence(
            ict_structure, strat_analysis, fvg_analysis
        )
        
        # Calculate scalp score
        scalp_ict_ict = ict_score
        scalp_strat_pts = strat_score
        scalp_fvg_pts = fvg_score
        scalp_confluence_pts = confluence_score
        
        scalp_score = int(
            (scalp_ict_ict * self.scalp_weights['ict_structure'] +
             scalp_strat_pts * self.scalp_weights['strat_alignment'] +
             scalp_fvg_pts * self.scalp_weights['fvg_freshness'] +
             scalp_confluence_pts * self.scalp_weights['confluence']) / 100
        )
        
        # Calculate swing score (may use slightly different context)
        swing_ict_pts = ict_score
        swing_strat_pts = strat_score
        swing_fvg_pts = fvg_score
        swing_confluence_pts = confluence_score
        
        swing_score = int(
            (swing_ict_pts * self.swing_weights['ict_structure'] +
             swing_strat_pts * self.swing_weights['strat_alignment'] +
             swing_fvg_pts * self.swing_weights['fvg_freshness'] +
             swing_confluence_pts * self.swing_weights['confluence']) / 100
        )
        
        # Determine structure quality
        structure_quality = self._determine_quality(
            ict_structure.trend_confidence,
            strat_analysis.confidence,
            ict_structure.displacement_detected
        )
        
        # Determine confluence level
        confluence_level = self._determine_confluence_level(confluence_score)
        
        return Scoring(
            scalp_score=scalp_score,
            swing_score=swing_score,
            structure_quality=structure_quality,
            confluence_level=confluence_level,
            scalp_ict_structure=scalp_ict_ict,
            scalp_strat_alignment=scalp_strat_pts,
            scalp_fvg_freshness=scalp_fvg_pts,
            scalp_confluence=scalp_confluence_pts,
            swing_ict_structure=swing_ict_pts,
            swing_strat_alignment=swing_strat_pts,
            swing_fvg_freshness=swing_fvg_pts,
            swing_confluence=swing_confluence_pts
        )
    
    def _score_ict_structure(self, ict_structure: ICTStructure) -> int:
        """
        Score ICT structure (0-100)
        
        Based on:
        - Trend confidence (0-100)
        - BOS/CHoCH conviction
        - Displacement detection
        """
        base_score = ict_structure.trend_confidence
        
        # Bonus points for BOS
        if ict_structure.bos_high or ict_structure.bos_low:
            base_score = min(100, base_score + 10)
        
        # Bonus points for displacement
        if ict_structure.displacement_detected:
            base_score = min(100, base_score + 10)
        
        # Penalty for neutral trend
        if ict_structure.trend_bias == TrendBias.NEUTRAL:
            base_score = max(30, base_score - 30)
        
        return base_score
    
    def _score_strat_alignment(self, strat_analysis: STRATAnalysis) -> int:
        """
        Score STRAT alignment (0-100)
        
        Based on:
        - Confidence (0-100)
        - Conflict detection
        - Pattern sequence quality
        """
        base_score = strat_analysis.confidence
        
        # Heavy penalty for conflict
        if strat_analysis.conflict_detected:
            base_score = max(30, base_score - 30)
        
        # Bonus for clear pattern (all Type 1 or dominant direction)
        type1_count = strat_analysis.pattern_sequence.count('1')
        type2_count = strat_analysis.pattern_sequence.count('2')
        type3_count = strat_analysis.pattern_sequence.count('3')
        
        total = len(strat_analysis.pattern_sequence)
        
        if total > 0 and type1_count / total > 0.7:
            base_score = min(100, base_score + 10)
        
        # Penalty for chop (too many Type 2 and 3)
        if total > 0 and (type2_count + type3_count) / total > 0.5:
            base_score = max(30, base_score - 20)
        
        return base_score
    
    def _score_fvg_freshness(self, fvg_analysis: FVGAnalysis) -> int:
        """
        Score FVG freshness (0-100)
        
        Based on:
        - Number of fresh FVGs
        - Number of untested FVGs
        - Gap sizes
        """
        score = 50
        
        # Bonus for fresh FVGs
        if fvg_analysis.fresh_fvgs:
            score += min(30, len(fvg_analysis.fresh_fvgs) * 10)
        
        # Bonus for untested FVGs
        if fvg_analysis.untested_fvgs:
            score += min(20, len(fvg_analysis.untested_fvgs) * 10)
        
        # Penalty if no FVGs
        if not fvg_analysis.fresh_fvgs and not fvg_analysis.untested_fvgs:
            score = max(30, score - 20)
        
        return min(100, score)
    
    def _calculate_confluence(
        self,
        ict_structure: ICTStructure,
        strat_analysis: STRATAnalysis,
        fvg_analysis: FVGAnalysis
    ) -> int:
        """
        Calculate confluence score (0-100)
        
        Confluence = alignment of signals across engines
        """
        aligned_engines = 0
        total_engines = 3
        
        # Check ICT bias
        if ict_structure.trend_bias in [TrendBias.BULLISH, TrendBias.BEARISH]:
            aligned_engines += 1
        
        # Check STRAT bias
        if strat_analysis.bias in [TrendBias.BULLISH, TrendBias.BEARISH]:
            aligned_engines += 1
        
        # Check FVG presence
        if fvg_analysis.fresh_fvgs or fvg_analysis.untested_fvgs:
            aligned_engines += 1
        
        # Check if biases align
        if (ict_structure.trend_bias == strat_analysis.bias and
            ict_structure.trend_bias != TrendBias.NEUTRAL):
            # Bonus for aligned biases
            return min(100, (aligned_engines / total_engines) * 100 + 15)
        
        return int((aligned_engines / total_engines) * 100)
    
    def _determine_quality(
        self,
        ict_confidence: int,
        strat_confidence: int,
        displacement_detected: bool
    ) -> str:
        """
        Determine structure quality rating (A, B, C)
        """
        avg_confidence = (ict_confidence + strat_confidence) / 2
        
        if avg_confidence >= 80 and displacement_detected:
            return 'A'
        elif avg_confidence >= 60:
            return 'B'
        else:
            return 'C'
    
    def _determine_confluence_level(self, confluence_score: int) -> str:
        """
        Determine confluence level (weak, moderate, strong)
        """
        if confluence_score >= 80:
            return 'strong'
        elif confluence_score >= 60:
            return 'moderate'
        else:
            return 'weak'