'use client';

import { QuestionData, ProgressData } from '@/lib/api';

interface QuestionCardProps {
  question: QuestionData;
  progress?: ProgressData;
  narrowingHistory: number[];
  confirmedClues: string[];
  onAnswer: (answerText: string) => Promise<void>;
  loading: boolean;
  referenceBanner?: string | null;
}

export default function QuestionCard({
  question,
  progress,
  narrowingHistory,
  confirmedClues,
  onAnswer,
  loading,
  referenceBanner,
}: QuestionCardProps) {
  const options = question.options || ["Yes", "No", "I don't remember"];

  return (
    <div className="card-container">
      {/* Reference Banner if returning from 'Looks close' flow */}
      {referenceBanner && (
        <div
          style={{
            background: 'rgba(56, 189, 248, 0.12)',
            border: '1px solid var(--accent-color)',
            borderRadius: '8px',
            padding: '0.75rem 1rem',
            marginBottom: '1.5rem',
            color: 'var(--accent-color)',
            fontSize: '0.9rem',
            fontWeight: 500,
          }}
        >
          💡 {referenceBanner}
        </div>
      )}

      {/* Narrowing Progress Header */}
      <div className="progress-banner">
        <span>Narrowing Candidates</span>
        <div className="progress-steps">
          {narrowingHistory.map((count, idx) => (
            <span key={idx} style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem' }}>
              {idx > 0 && <span className="progress-arrow">→</span>}
              <span
                style={{
                  color: idx === narrowingHistory.length - 1 ? '#ffffff' : 'var(--text-secondary)',
                  fontWeight: idx === narrowingHistory.length - 1 ? 700 : 500,
                }}
              >
                {count}
              </span>
            </span>
          ))}
          {progress?.activeCandidates !== undefined &&
            narrowingHistory[narrowingHistory.length - 1] !== progress.activeCandidates && (
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem' }}>
                <span className="progress-arrow">→</span>
                <span style={{ color: '#ffffff', fontWeight: 700 }}>{progress.activeCandidates}</span>
              </span>
            )}
        </div>
      </div>

      {/* Confirmed Clue Chips */}
      {confirmedClues.length > 0 && (
        <div style={{ marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Confirmed clues:</span>
          {confirmedClues.map((clue, idx) => (
            <span
              key={idx}
              style={{
                fontSize: '0.8rem',
                background: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                color: 'var(--success-color)',
                padding: '0.2rem 0.6rem',
                borderRadius: '999px',
              }}
            >
              {clue} ✓
            </span>
          ))}
        </div>
      )}

      {/* Main Question Experience */}
      <div className="question-card">
        <div className="question-callout">
          <span>🧠</span>
          <span>Memory Guide chose this question based on the photos still in consideration.</span>
        </div>

        <h2 className="question-text">{question.text}</h2>

        <div className="options-grid">
          {options.map((opt, idx) => {
            const isIdk = opt.toLowerCase().includes("don't remember") || opt.toLowerCase().includes("idk");
            return (
              <button
                key={idx}
                className={`btn-option ${isIdk ? 'btn-idk' : ''}`}
                onClick={() => onAnswer(opt)}
                disabled={loading}
              >
                <span>{opt}</span>
                {!isIdk && <span style={{ opacity: 0.6 }}>→</span>}
              </button>
            );
          })}
        </div>
      </div>

      {loading && (
        <div className="loading-container" style={{ padding: '1.5rem 0' }}>
          <div className="spinner" />
          <p className="loading-text">Thinking about which clue would help most…</p>
        </div>
      )}
    </div>
  );
}
