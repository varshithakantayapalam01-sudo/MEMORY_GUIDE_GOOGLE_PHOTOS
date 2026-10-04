'use client';

import React, { useState } from 'react';
import { CandidateData } from '@/lib/api';

interface RecognitionGridProps {
  candidates: CandidateData[];
  onSelectFound: (imageId: string) => Promise<void>;
  onSelectClose: (imageId: string) => Promise<void>;
  onSelectNone: () => Promise<void>;
  loading: boolean;
}

export default function RecognitionGrid({
  candidates,
  onSelectFound,
  onSelectClose,
  onSelectNone,
  loading,
}: RecognitionGridProps) {
  const [noneClickedMessage, setNoneClickedMessage] = useState<string | null>(null);

  const handleNoneClick = async () => {
    setNoneClickedMessage("Okay — I'll keep looking.");
    await onSelectNone();
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div style={{ background: '#F8FAFC', border: '1px solid #E2E8F0', padding: '16px', borderRadius: '16px' }}>
        <h3 style={{ fontSize: '18px', fontWeight: 700, color: '#0F172A', marginBottom: '4px' }}>
          Do you recognize it?
        </h3>
        <p style={{ fontSize: '13px', color: '#64748B' }}>
          Memory Guide narrowed your library to these remaining candidates.
        </p>
      </div>

      {noneClickedMessage && (
        <div style={{
          background: '#FEF3C7',
          border: '1px solid #FCD34D',
          color: '#92400E',
          padding: '10px 14px',
          borderRadius: '12px',
          fontSize: '13px',
          fontWeight: 500
        }}>
          🔍 {noneClickedMessage}
        </div>
      )}

      {/* 2-3 column candidate photo grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(130px, 1fr))',
        gap: '12px'
      }}>
        {candidates.map((candidate) => (
          <div
            key={candidate.imageId}
            style={{
              background: '#FFFFFF',
              border: '1px solid #E2E8F0',
              borderRadius: '12px',
              overflow: 'hidden',
              display: 'flex',
              flexDirection: 'column',
              boxShadow: '0 2px 4px rgba(0,0,0,0.04)'
            }}
          >
            <div style={{ aspectRatio: '1/1', overflow: 'hidden', background: '#F1F5F9' }}>
              <img
                src={candidate.imageUrl}
                alt={`Candidate ${candidate.imageId}`}
                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                onError={(e) => {
                  (e.target as HTMLImageElement).src = `https://picsum.photos/seed/${candidate.imageId}/300/300`;
                }}
              />
            </div>
            <div style={{ padding: '8px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
              <button
                className="btn-primary"
                style={{ width: '100%', padding: '6px', fontSize: '12px', borderRadius: '8px', justifyContent: 'center' }}
                onClick={() => onSelectFound(candidate.imageId)}
                disabled={loading}
              >
                This is it
              </button>
              <button
                className="btn-secondary"
                style={{ width: '100%', padding: '6px', fontSize: '11px', borderRadius: '8px', justifyContent: 'center' }}
                onClick={() => onSelectClose(candidate.imageId)}
                disabled={loading}
              >
                Looks close
              </button>
            </div>
          </div>
        ))}
      </div>

      <button
        className="btn-ghost"
        style={{
          width: '100%',
          padding: '12px',
          border: '1px dashed #CBD5E1',
          borderRadius: '12px',
          color: '#64748B',
          fontSize: '13px',
          fontWeight: 500,
          marginTop: '4px'
        }}
        onClick={handleNoneClick}
        disabled={loading}
      >
        None of these
      </button>

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
          <span>Updating candidates…</span>
        </div>
      )}
    </div>
  );
}
