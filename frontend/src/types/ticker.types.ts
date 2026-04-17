/**
 * Ticker Data Types
 */

export interface TickerPriceData {
  symbol: string;
  official_close: {
    price: number;
    date: string;
    is_regular_session: boolean;
    source: string;
  };
  after_hours: {
    price: number | null;
    change_from_close: number | null;
    change_percent: number | null;
    timestamp: string | null;
    source: string;
  };
  premarket: {
    price: number | null;
    change_from_close: number | null;
    change_percent: number | null;
    timestamp: string | null;
    source: string;
  };
  live: {
    price: number | null;
    change_from_close: number | null;
    change_percent: number | null;
    timestamp: string | null;
    source: string;
  };
  opening_range: {
    high: number | null;
    low: number | null;
    midpoint: number | null;
  };
  vwap: {
    price: number | null;
  };
  differences: {
    after_hours_vs_close: number | null;
    premarket_vs_close: number | null;
    live_vs_close: number | null;
    premarket_vs_after_hours: number | null;
    live_vs_premarket: number | null;
  };
  last_updated: string;
  data_quality: string;
  session_type: string;
}

export interface OHLCVCandle {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface OHLCVSeries {
  symbol: string;
  timeframe: string;
  candles: OHLCVCandle[];
}