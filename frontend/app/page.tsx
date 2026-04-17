/**
 * Main Dashboard Page
 */
'use client';

import React, { useEffect, useState } from 'react';
import { getPriceData, runPrepAnalysis, runLiveAnalysis } from '../src/lib/api';
import { useTickerStore } from '../src/store/tickerStore';
import PriceBaseline from '../src/components/PriceBaseline';
import SetupQualityBars from '../src/components/SetupQualityBars';

export default function DashboardPage() {
  const { tickers, setTickers, loading, setLoading, error, setError } = useTickerStore();
  const [selectedTicker, setSelectedTicker] = useState<string>('NVDA');
  const [activeMode, setActiveMode] = useState<'prep' | 'live'>('live');
  const [selectedAnalysis, setSelectedAnalysis] = useState<any>(null);

  const watchlist = ['NVDA', 'META', 'TSLA', 'AAPL', 'GOOGL', 'AMZN', 'MSFT'];

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getBatchPriceData(watchlist);
      setTickers(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectTicker = (symbol: string) => {
    setSelectedTicker(symbol);
  };

  const handleRunPrepAnalysis = async () => {
    setLoading(true);
    setError(null);
    try {
      const results = await runPrepAnalysis([selectedTicker]);
      setSelectedAnalysis(results[selectedTicker]);
    } catch (err: any) {
      setError(err.message || 'Failed to run analysis');
    } finally {
      setLoading(false);
    }
  };

  const handleRunLiveAnalysis = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await runLiveAnalysis(selectedTicker);
      setSelectedAnalysis(result);
    } catch (err: any) {
      setError(err.message || 'Failed to run analysis');
    } finally {
      setLoading(false);
    }
  };

  const selectedTickerData = tickers.find((t: any) => t.symbol === selectedTicker);

  return (
    <main className="min-h-screen bg-background-dark text-white p-4">
      {/* Header */}
      <header className="mb-6 border-b border-gray-800 pb-4">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold">Trading Dashboard</h1>
            <p className="text-gray-400 text-sm">Production-Grade Options Analysis</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setActiveMode('prep')}
              className={`px-4 py-2 rounded ${
                activeMode === 'prep'
                  ? 'bg-accent-primary text-white'
                  : 'bg-background-card text-gray-400 hover:text-white'
              }`}
            >
              Prep Mode
            </button>
            <button
              onClick={() => setActiveMode('live')}
              className={`px-4 py-2 rounded ${
                activeMode === 'live'
                  ? 'bg-accent-primary text-white'
                  : 'bg-background-card text-gray-400 hover:text-white'
              }`}
            >
              Live Mode
            </button>
          </div>
        </div>
      </header>

      {/* Error Banner */}
      {error && (
        <div className="mb-4 p-3 bg-red-500/20 border border-red-500 rounded text-red-400">
          {error}
        </div>
      )}

      {/* Main Content */}
      <div className="grid grid-cols-12 gap-4">
        {/* Left Sidebar - Ticker List */}
        <div className="col-span-3 space-y-2">
          <div className="bg-background-card rounded-lg p-3">
            <h2 className="text-sm font-semibold text-gray-400 mb-3">WATCHLIST</h2>
            <div className="space-y-1">
              {watchlist.map((symbol) => (
                <button
                  key={symbol}
                  onClick={() => handleSelectTicker(symbol)}
                  className={`w-full text-left px-3 py-2 rounded text-sm transition-colors ${
                    selectedTicker === symbol
                      ? 'bg-accent-primary text-white'
                      : 'bg-background-lighter text-gray-400 hover:bg-background-card hover:text-white'
                  }`}
                >
                  {symbol}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Main Area */}
        <div className="col-span-9 grid grid-cols-2 gap-4">
          {/* Price Baseline */}
          {selectedTickerData && (
            <div className="col-span-2">
              <PriceBaseline data={selectedTickerData} />
            </div>
          )}

          {/* Action Buttons */}
          <div className="col-span-2 flex gap-2">
            <button
              onClick={handleRunPrepAnalysis}
              disabled={loading}
              className="px-6 py-2 bg-accent-secondary hover:bg-purple-600 text-white rounded disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Analyzing...' : 'Run Prep Analysis'}
            </button>
            <button
              onClick={handleRunLiveAnalysis}
              disabled={loading}
              className="px-6 py-2 bg-accent-primary hover:bg-blue-600 text-white rounded disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Analyzing...' : 'Run Live Analysis'}
            </button>
          </div>

          {/* Analysis Results */}
          {selectedAnalysis && selectedAnalysis.scoring && (
            <div className="col-span-2">
              <SetupQualityBars scoring={selectedAnalysis.scoring} />
            </div>
          )}

          {/* Loading State */}
          {loading && (
            <div className="col-span-2 text-center py-8">
              <div className="text-gray-400">Loading...</div>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}