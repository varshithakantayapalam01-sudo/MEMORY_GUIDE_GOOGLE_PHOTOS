'use client';

import React from 'react';
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
  const currentCount = progress?.activeCandidates ?? narrowingHistory[narrowingHistory.length - 1] ?? 12;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {/* Reference Banner if coming from 'Looks close' */}
      {referenceBanner && (
        <div style={{
          background: '#E0F2FE',
          border: '1px solid #7DD3FC',
          borderRadius: '12px',
          padding: '10px 14px',
          color: '#0369A1',
          fontSize: '13px',
          fontWeight: 500,
          display: 'flex',
          alignItems: 'center',
          gap: '6px'
        }}>
          <span>💡</span>
          <span>{referenceBanner}</span>
        </div>
      )}

      {/* Progress & Candidate Badge */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: '#F8FAFC',
        border: '1px solid #E2E8F0',
        padding: '10px 14px',
        borderRadius: '12px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', color: '#64748B' }}>
          <span>Candidate progress:</span>
          <span style={{ fontWeight: 600, color: '#1E293B' }}>
            {narrowingHistory.join(' → ')} {narrowingHistory.length === 1 ? 'photos' : ''}
          </span>
        </div>
        <span style={{
          background: '#1A73E8',
          color: '#FFFFFF',
          fontSize: '12px',
          fontWeight: 600,
          padding: '3px 10px',
          borderRadius: '12px'
        }}>
          {currentCount} possible
        </span>
      </div>

      {/* Dynamic Confirmed / Identified Clue Chips */}
      {confirmedClues.length > 0 && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
          {confirmedClues.map((clue, idx) => (
            <span key={idx} className="clue-chip confirmed">
              {clue} ✓
            </span>
          ))}
        </div>
      )}

      {/* Question Card */}
      <div style={{
        background: '#FFFFFF',
        border: '1px solid #E2E8F0',
        borderRadius: '16px',
        padding: '20px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
        display: 'flex',
        flexDirection: 'column',
        gap: '14px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#1A73E8', fontSize: '13px', fontWeight: 600 }}>
          <span>✨</span>
          <span>Memory Guide</span>
        </div>

        <h3 style={{ fontSize: '18px', fontWeight: 700, color: '#0F172A', lineHeight: 1.3 }}>
          "{question.text}"
        </h3>

        <p style={{ fontSize: '12px', color: '#64748B', lineHeight: 1.4 }}>
          Chosen because this detail best separates the photos still in consideration.
        </p>

        {/* Options */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '6px' }}>
          {options.map((opt, idx) => {
            const isIdk = opt.toLowerCase().includes("don't remember") || opt.toLowerCase().includes("idk");
            return (
              <button
                key={idx}
                className={isIdk ? 'btn-secondary' : 'btn-primary'}
                style={{
                  justifyContent: 'space-between',
                  width: '100%',
                  padding: '12px 16px',
                  borderRadius: '12px',
                  fontSize: '14px',
                  opacity: loading ? 0.7 : 1,
                  cursor: loading ? 'not-allowed' : 'pointer'
                }}
                onClick={() => onAnswer(opt)}
                disabled={loading}
              >
                <span>{opt}</span>
                <span>{isIdk ? '❓' : '→'}</span>
              </button>
            );
          })}
        </div>
      </div>

      {loading && (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px', padding: '12px', color: '#64748B', fontSize: '13px' }}>
          <div style={{
            width: '18px',
            height: '18px',
            border: '2px solid #CBD5E1',
            borderTopColor: '#1A73E8',
            borderRadius: '50%',
            animation: 'spin 0.8s linear infinite'
          }} />
          <span>One detail could narrow this down…</span>
        </div>
      )}
    </div>
  );
}
