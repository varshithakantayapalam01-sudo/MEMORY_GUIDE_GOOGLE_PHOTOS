'use client';

import { useState } from 'react';
import { SelectionMetadata, ProgressData } from '@/lib/api';

interface ResearchDebugTraceProps {
  metadata?: SelectionMetadata;
  progress?: ProgressData;
  round?: number;
}

export default function ResearchDebugTrace({ metadata, progress, round }: ResearchDebugTraceProps) {
  const [collapsed, setCollapsed] = useState(false);

  if (!metadata && !progress) return null;

  return (
    <div className="debug-card">
      <div className="debug-title" onClick={() => setCollapsed(!collapsed)}>
        <span>🔬 RESEARCH DEBUG TRACE {round ? `(Round ${round})` : ''}</span>
        <span>{collapsed ? '▶ Show' : '▼ Hide'}</span>
      </div>

      {!collapsed && (
        <div className="debug-grid">
          {metadata?.dimension && (
            <div className="debug-item">
              <div className="debug-label">Selected Dimension</div>
              <div className="debug-val">{metadata.subattributeKey || metadata.dimension}</div>
            </div>
          )}

          {metadata?.discriminationScore !== undefined && (
            <div className="debug-item">
              <div className="debug-label">Discrimination Score</div>
              <div className="debug-val">{metadata.discriminationScore.toFixed(3)}</div>
            </div>
          )}

          {metadata?.memorabilityWeight !== undefined && (
            <div className="debug-item">
              <div className="debug-label">Memorability Weight</div>
              <div className="debug-val">{metadata.memorabilityWeight.toFixed(2)}</div>
            </div>
          )}

          {metadata?.finalScore !== undefined && (
            <div className="debug-item">
              <div className="debug-label">Final Question Score</div>
              <div className="debug-val">{metadata.finalScore.toFixed(3)}</div>
            </div>
          )}

          {progress && (
            <div className="debug-item">
              <div className="debug-label">Candidate Counts</div>
              <div className="debug-val">
                Active: {progress.activeCandidates} | Reserve: {progress.reserveCandidates}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
