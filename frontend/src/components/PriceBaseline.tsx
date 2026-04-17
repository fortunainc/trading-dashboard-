/**
 * Price Baseline Component
 * Displays all four price types explicitly separated
 */
import React from 'react';
import { TickerPriceData } from '../types/ticker.types';

interface PriceBaselineProps {
  data: TickerPriceData;
}

const PriceBaseline: React.FC<PriceBaselineProps> = ({ data }) => {
  const formatPrice = (price: number | null) => {
    if (price === null) return '--';
    return `$${price.toFixed(2)}`;
  };

  const formatChange = (change: number | null, percent: number | null) => {
    if (change === null || percent === null) return '--';
    const isPositive = change >= 0;
    return (
      <span className={isPositive ? 'text-green-500' : 'text-red-500'}>
        {isPositive ? '+' : ''}{change.toFixed(2)} ({isPositive ? '+' : ''}{percent.toFixed(2)}%)
      </span>
    );
  };

  return (
    <div className="bg-background-card rounded-lg p-4 space-y-3">
      <h3 className="text-lg font-semibold text-white mb-3">Price Baseline</h3>
      
      {/* Official Close */}
      <div className="flex justify-between items-center p-2 bg-background-lighter rounded">
        <div>
          <div className="text-sm text-gray-400">Official Close</div>
          <div className="text-xs text-gray-500">{data.official_close.date} • {data.official_close.source}</div>
        </div>
        <div className="text-right">
          <div className="text-xl font-bold text-white">{formatPrice(data.official_close.price)}</div>
          <div className="text-xs text-gray-500">Regular Session</div>
        </div>
      </div>

      {/* After Hours */}
      <div className="flex justify-between items-center p-2 bg-background-lighter rounded">
        <div>
          <div className="text-sm text-gray-400">After Hours</div>
          <div className="text-xs text-gray-500">{data.after_hours.timestamp}</div>
        </div>
        <div className="text-right">
          <div className="text-lg font-semibold text-white">{formatPrice(data.after_hours.price)}</div>
          <div className="text-sm">{formatChange(data.after_hours.change_from_close, data.after_hours.change_percent)}</div>
        </div>
      </div>

      {/* Premarket */}
      <div className="flex justify-between items-center p-2 bg-background-lighter rounded">
        <div>
          <div className="text-sm text-gray-400">Premarket</div>
          <div className="text-xs text-gray-500">{data.premarket.timestamp}</div>
        </div>
        <div className="text-right">
          <div className="text-lg font-semibold text-white">{formatPrice(data.premarket.price)}</div>
          <div className="text-sm">{formatChange(data.premarket.change_from_close, data.premarket.change_percent)}</div>
        </div>
      </div>

      {/* Live Price */}
      {data.live.price !== null && (
        <div className="flex justify-between items-center p-2 bg-accent-primary/20 rounded border border-accent-primary/50">
          <div>
            <div className="text-sm font-semibold text-white">Live Price</div>
            <div className="text-xs text-gray-500">{data.live.timestamp}</div>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-accent-primary">{formatPrice(data.live.price)}</div>
            <div className="text-sm font-semibold">{formatChange(data.live.change_from_close, data.live.change_percent)}</div>
          </div>
        </div>
      )}

      {/* Session Type */}
      <div className="text-center text-sm text-gray-400">
        Session: <span className="font-semibold text-white capitalize">{data.session_type}</span>
      </div>
    </div>
  );
};

export default PriceBaseline;