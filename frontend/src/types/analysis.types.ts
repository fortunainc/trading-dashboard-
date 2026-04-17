/**
 * Analysis Data Types
 */

export type TrendBias = 'bullish' | 'bearish' | 'neutral' | 'mixed';
export type SetupType = 'bullish_continuation' | 'bearish_continuation' | 'bullish_reversal' | 'bearish_reversal' | 'none';

export interface ICTStructure {
  trend_bias: TrendBias;
  trend_confidence: number;
  bos_high: number | null;
  bos_low: number | null;
  most_recent_high: number | null;
  most_recent_low: number | null;
  displacement_detected: boolean;
  displacement_magnitude: number | null;
  liquidity_sweeps: Array<{
    type: string;
    level: number;
    timestamp: string;
    strength: string;
  }>;
}

export interface STRATCandle {
  candle_index: number;
  timestamp: string;
  candle_type: string;
  body_percent: number;
  upper_wick_percent: number;
  lower_wick_percent: number;
  classification: string;
  is_bullish: boolean;
}

export interface STRATAnalysis {
  bias: TrendBias;
  confidence: number;
  classified_candles: STRATCandle[];
  pattern_sequence: string;
  conflict_detected: boolean;
  conflict_details: string | null;
}

export interface FVG {
  type: 'bullish' | 'bearish';
  high: number;
  low: number;
  gap_percent: number;
  created_at: string;
  tested: boolean;
  test_count: number;
}

export interface FVGAnalysis {
  fresh_fvgs: FVG[];
  ageing_fvgs: FVG[];
  stale_fvgs: FVG[];
  untested_fvgs: FVG[];
}

export interface Scoring {
  scalp_score: number;
  swing_score: number;
  structure_quality: 'A' | 'B' | 'C';
  confluence_level: 'weak' | 'moderate' | 'strong';
  scalp_ict_structure: number;
  scalp_strat_alignment: number;
  scalp_fvg_freshness: number;
  scalp_confluence: number;
  swing_ict_structure: number;
  swing_strat_alignment: number;
  swing_fvg_freshness: number;
  swing_confluence: number;
}

export interface CompleteAnalysis {
  symbol: string;
  timestamp: string;
  official_close: number;
  ict_analysis: ICTStructure;
  strat_analysis: STRATAnalysis;
  fvg_analysis: FVGAnalysis;
  hard_filter_passed: boolean;
  filter_reasons: string[];
  scoring: Scoring | null;
  setup_type: SetupType;
  scalp_contracts: Contract[];
  swing_contracts: Contract[];
  prep_thesis: string | null;
}

export interface Contract {
  rank: number;
  contract: string;
  dte: number;
  delta: number;
  bid: number;
  ask: number;
  spread_percent: number;
  volume: number;
  open_interest: number;
  iv: number;
  liquidity_grade: string;
  rationale: string;
  entry_limit: number;
  target: number;
  stop_loss: number;
}

export interface ThesisValidation {
  status: 'VALIDATED' | 'INVALIDATED' | 'UNCERTAIN';
  confidence: number;
  changes: string[];
  entry_plan: string;
}

export interface TriggerStatus {
  scalp_trigger: {
    status: string;
    condition: string;
    time_remaining: number;
  };
  swing_trigger: {
    status: string;
    condition: string;
    time_remaining: string;
  };
}