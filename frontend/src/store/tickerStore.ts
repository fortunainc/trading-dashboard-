/**
 * Ticker Data Store - State Management
 */
import { create } from 'zustand';
import { TickerPriceData, CompleteAnalysis } from '../types';

interface TickerStore {
  // State
  tickers: TickerPriceData[];
  analyses: Map<string, CompleteAnalysis>;
  selectedTicker: string | null;
  loading: boolean;
  error: string | null;

  // Actions
  tickersLoaded: boolean;
  setTickers: (tickers: TickerPriceData[]) => void;
  updateTicker: (symbol: string, data: Partial<TickerPriceData>) => void;
  selectTicker: (symbol: string | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setAnalysis: (symbol: string, analysis: CompleteAnalysis) => void;
  getAnalysis: (symbol: string) => CompleteAnalysis | undefined;
}

export const useTickerStore = create<TickerStore>((set, get) => ({
  // Initial State
  tickers: [],
  analyses: new Map(),
  selectedTicker: null,
  loading: false,
  error: null,
  tickersLoaded: false,

  // Actions
  setTickers: (tickers) => set({ tickers, tickersLoaded: true }),

  updateTicker: (symbol, data) =>
    set((state) => ({
      tickers: state.tickers.map((ticker) =>
        ticker.symbol === symbol ? { ...ticker, ...data } : ticker
      ),
    })),

  selectTicker: (symbol) => set({ selectedTicker: symbol }),

  setLoading: (loading) => set({ loading }),

  setError: (error) => set({ error }),

  setAnalysis: (symbol, analysis) =>
    set((state) => {
      const newAnalyses = new Map(state.analyses);
      newAnalyses.set(symbol, analysis);
      return { analyses: newAnalyses };
    }),

  getAnalysis: (symbol) => get().analyses.get(symbol),
}));