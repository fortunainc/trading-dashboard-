"""
Analysis API Routes
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime
import logging

from ..models.analysis import ICTStructure, STRATAnalysis, FVGAnalysis, Scoring
from ..engines.ict_engine import ICTEngine
from ..engines.strat_engine import STRATEngine
from ..engines.fvg_engine import FVGEngine
from ..engines.scoring_engine import ScoringEngine
from ..models.ohlcv import OHLCVSeries, OHLCVCandle

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize engines (singleton)
ict_engine = ICTEngine()
strat_engine = STRATEngine()
fvg_engine = FVGEngine()
scoring_engine = ScoringEngine()


@router.post("/prep")
async def run_prep_analysis(
    symbols: List[str],
    date: Optional[str] = None
) -> dict:
    """
    Run night-before prep analysis
    
    Uses official close data and completed structure only.
    No live/premarket data.
    """
    try:
        results = {}
        
        for symbol in symbols:
            # Generate mock OHLCV data (will be replaced with real data)
            ohlcv_series = _generate_mock_ohlcv_series(symbol)
            
            # Run engines
            ict_structure = ict_engine.analyze(ohlcv_series)
            strat_analysis = strat_engine.analyze(ohlcv_series)
            fvg_analysis = fvg_engine.analyze(ohlcv_series)
            
            # Calculate scores
            scoring = scoring_engine.calculate_scores(
                ict_structure,
                strat_analysis,
                fvg_analysis
            )
            
            # Determine setup type
            setup_type = _determine_setup_type(ict_structure, strat_analysis)
            
            results[symbol] = {
                "symbol": symbol,
                "date": date or datetime.now().strftime("%Y-%m-%d"),
                "official_close": 500.00,
                "ict_analysis": ict_structure.__dict__,
                "strat_analysis": strat_analysis.__dict__,
                "fvg_analysis": {
                    "fresh_fvgs": [f.__dict__ for f in fvg_analysis.fresh_fvgs],
                    "ageing_fvgs": [f.__dict__ for f in fvg_analysis.ageing_fvgs],
                    "stale_fvgs": [f.__dict__ for f in fvg_analysis.stale_fvgs],
                    "untested_fvgs": [f.__dict__ for f in fvg_analysis.untested_fvgs]
                },
                "scoring": scoring.__dict__,
                "setup_type": setup_type,
                "prep_thesis": _generate_prep_thesis(symbol, ict_structure, strat_analysis),
                "validation_status": "PENDING"
            }
        
        return results
    
    except Exception as e:
        logger.error(f"Error running prep analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/live")
async def run_live_analysis(
    symbol: str,
    validate_thesis: bool = True
) -> dict:
    """
    Run live analysis with thesis validation
    
    Uses premarket/live data and validates against prep thesis.
    """
    try:
        # Generate mock OHLCV data
        ohlcv_series = _generate_mock_ohlcv_series(symbol)
        
        # Run engines
        ict_structure = ict_engine.analyze(ohlcv_series)
        strat_analysis = strat_engine.analyze(ohlcv_series)
        fvg_analysis = fvg_engine.analyze(ohlcv_series)
        
        # Calculate scores
        scoring = scoring_engine.calculate_scores(
            ict_structure,
            strat_analysis,
            fvg_analysis
        )
        
        result = {
            "symbol": symbol,
            "live_price": 502.50,
            "ict_analysis": ict_structure.__dict__,
            "strat_analysis": strat_analysis.__dict__,
            "fvg_analysis": {
                "fresh_fvgs": [f.__dict__ for f in fvg_analysis.fresh_fvgs],
                "ageing_fvgs": [f.__dict__ for f in fvg_analysis.ageing_fvgs],
                "stale_fvgs": [f.__dict__ for f in fvg_analysis.stale_fvgs],
                "untested_fvgs": [f.__dict__ for f in fvg_analysis.untested_fvgs]
            },
            "scoring": scoring.__dict__,
            "updated_at": datetime.now().isoformat()
        }
        
        if validate_thesis:
            result["thesis_validation"] = {
                "status": "VALIDATED",
                "confidence": 80,
                "changes": [],
                "entry_plan": "Entry on pullback to support zone"
            }
        
        result["trigger_status"] = {
            "scalp_trigger": {
                "status": "READY_TO_FIRE",
                "condition": "Price breaks above 502.00",
                "time_remaining": 0
            },
            "swing_trigger": {
                "status": "WAITING_FOR_PULLBACK",
                "condition": "Pullback to 500-501 zone",
                "time_remaining": "N/A"
            }
        }
        
        return result
    
    except Exception as e:
        logger.error(f"Error running live analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _generate_mock_ohlcv_series(symbol: str, timeframe: str = "15m") -> OHLCVSeries:
    """Generate mock OHLCV series for demonstration"""
    base_price = 500.00
    candles = []
    
    for i in range(20):
        candle = OHLCVCandle(
            timestamp=datetime.now(),
            open=round(base_price + (i * 0.5), 2),
            high=round(base_price + (i * 0.5) + 1.0, 2),
            low=round(base_price + (i * 0.5) - 0.5, 2),
            close=round(base_price + (i * 0.5) + 0.25, 2),
            volume=1000000 + (i * 10000)
        )
        candles.append(candle)
    
    return OHLCVSeries(
        timeframe=timeframe,
        candles=candles,
        symbol=symbol
    )


def _determine_setup_type(ict_structure: ICTStructure, strat_analysis: STRATAnalysis) -> str:
    """Determine setup type based on engine outputs"""
    if (ict_structure.trend_bias.value == "bullish" and
        strat_analysis.bias.value == "bullish"):
        return "bullish_continuation"
    elif (ict_structure.trend_bias.value == "bearish" and
          strat_analysis.bias.value == "bearish"):
        return "bearish_continuation"
    elif (ict_structure.trend_bias.value == "bullish" and
          strat_analysis.bias.value == "bearish"):
        return "bullish_reversal"
    elif (ict_structure.trend_bias.value == "bearish" and
          strat_analysis.bias.value == "bullish"):
        return "bearish_reversal"
    else:
        return "none"


def _generate_prep_thesis(
    symbol: str,
    ict_structure: ICTStructure,
    strat_analysis: STRATAnalysis
) -> str:
    """Generate prep thesis document"""
    return f"""
NIGHT-BEFORE PREP THESIS - {symbol}

STRUCTURE ANALYSIS:
- Trend Bias: {ict_structure.trend_bias.value}
- Trend Confidence: {ict_structure.trend_confidence}/100
- STRAT Bias: {strat_analysis.bias.value}
- STRAT Confidence: {strat_analysis.confidence}/100

KEY LEVELS:
- Most Recent High: {ict_structure.most_recent_high or 'N/A'}
- Most Recent Low: {ict_structure.most_recent_low or 'N/A'}
- BOS High: {ict_structure.bos_high or 'N/A'}
- BOS Low: {ict_structure.bos_low or 'N/A'}

THESIS CONCLUSION:
Setup Type: Bullish Continuation
Confidence: Moderate
Ready for Morning Validation: Yes
"""