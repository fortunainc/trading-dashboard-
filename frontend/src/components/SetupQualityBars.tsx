/**
 * Setup Quality Bars Component
 * Displays scoring breakdown with explainable components
 */
import React from 'react';
import { Scoring } from '../types/analysis.types';

interface SetupQualityBarsProps {
  scoring: Scoring;
}

const SetupQualityBars: React.FC<SetupQualityBarsProps> = ({ scoring }) => {
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getQualityColor = (grade: string) => {
    if (grade === 'A') return 'text-green-500';
    if (grade === 'B') return 'text-yellow-500';
    return 'text-red-500';
  };

  const getConfluenceColor = (level: string) => {
    if (level === 'strong') return 'text-green-500';
    if (level === 'moderate') return 'text-yellow-500';
    return 'text-red-500';
  };

  return (
    <div className="bg-background-card rounded-lg p-4 space-y-4">
      <h3 className="text-lg font-semibold text-white">Setup Quality</h3>

      {/* Overall Scores */}
      <div className="grid grid-cols-2 gap-4">
        {/* Scalp Score */}
        <div className="bg-background-lighter rounded p-3">
          <div className="text-sm text-gray-400 mb-2">Scalp Score</div>
          <div className="text-3xl font-bold text-white">{scoring.scalp_score}/100</div>
          <div className="mt-2 w-full bg-gray-700 rounded-full h-2">
            <div
              className={`h-2 rounded-full ${getScoreColor(scoring.scalp_score)}`}
              style={{ width: `${scoring.scalp_score}%` }}
            ></div>
          </div>
        </div>

        {/* Swing Score */}
        <div className="bg-background-lighter rounded p-3">
          <div className="text-sm text-gray-400 mb-2">Swing Score</div>
          <div className="text-3xl font-bold text-white">{scoring.swing_score}/100</div>
          <div className="mt-2 w-full bg-gray-700 rounded-full h-2">
            <div
              className={`h-2 rounded-full ${getScoreColor(scoring.swing_score)}`}
              style={{ width: `${scoring.swing_score}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* Structure Quality & Confluence */}
      <div className="grid grid-cols-2 gap-4">
        <div className="text-center">
          <div className="text-sm text-gray-400 mb-1">Structure Quality</div>
          <div className={`text-4xl font-bold ${getQualityColor(scoring.structure_quality)}`}>
            {scoring.structure_quality}
          </div>
        </div>
        <div className="text-center">
          <div className="text-sm text-gray-400 mb-1">Confluence</div>
          <div className={`text-xl font-bold capitalize ${getConfluenceColor(scoring.confluence_level)}`}>
            {scoring.confluence_level}
          </div>
        </div>
      </div>

      {/* Scalp Score Breakdown */}
      <div>
        <div className="text-sm text-gray-400 mb-2">Scalp Score Breakdown</div>
        <div className="space-y-2">
          <div>
            <div className="flex justify-between text-xs text-gray-300 mb-1">
              <span>ICT Structure (30%)</span>
              <span>{scoring.scalp_ict_structure}/100</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-1.5">
              <div
                className={`h-1.5 rounded-full ${getScoreColor(scoring.scalp_ict_structure)}`}
                style={{ width: `${scoring.scalp_ict_structure}%` }}
              ></div>
            </div>
          </div>
          <div>
            <div className="flex justify-between text-xs text-gray-300 mb-1">
              <span>STRAT Alignment (30%)</span>
              <span>{scoring.scalp_strat_alignment}/100</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-1.5">
              <div
                className={`h-1.5 rounded-full ${getScoreColor(scoring.scalp_strat_alignment)}`}
                style={{ width: `${scoring.scalp_strat_alignment}%` }}
              ></div>
            </div>
          </div>
          <div>
            <div className="flex justify-between text-xs text-gray-300 mb-1">
              <span>FVG Freshness (20%)</span>
              <span>{scoring.scalp_fvg_freshness}/100</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-1.5">
              <div
                className={`h-1.5 rounded-full ${getScoreColor(scoring.scalp_fvg_freshness)}`}
                style={{ width: `${scoring.scalp_fvg_freshness}%` }}
              ></div>
            </div>
          </div>
          <div>
            <div className="flex justify-between text-xs text-gray-300 mb-1">
              <span>Confluence (20%)</span>
              <span>{scoring.scalp_confluence}/100</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-1.5">
              <div
                className={`h-1.5 rounded-full ${getScoreColor(scoring.scalp_confluence)}`}
                style={{ width: `${scoring.scalp_confluence}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SetupQualityBars;