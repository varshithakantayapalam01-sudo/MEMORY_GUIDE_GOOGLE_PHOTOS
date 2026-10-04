'use client';

import React, { useState } from 'react';
import { FoundSummary, SelectionMetadata } from '@/lib/api';
import { DEMO_PHOTOS } from '@/lib/demoFallbackEngine';

interface FoundOutcomeProps {
  selectedImageId?: string;
  summary?: FoundSummary;
  narrowingPathStr: string;
  onSubmitFeedback: (rating: number, confusingFeedback?: string) => Promise<void>;
  onRestart: () => void;
  loading: boolean;
  selectionMetadata?: SelectionMetadata;
  showDebug?: boolean;
}

export default function FoundOutcome({
  selectedImageId,
  summary,
  narrowingPathStr,
  onSubmitFeedback,
  onRestart,
  loading,
  selectionMetadata,
  showDebug,
}: FoundOutcomeProps) {
  const [showExplanation, setShowExplanation] = useState(false);
  const [feedbackRating, setFeedbackRating] = useState<number | null>(null);

  const targetPhoto = DEMO_PHOTOS.find(p => p.image_id === selectedImageId) || DEMO_PHOTOS[0];
  const questionsAsked = summary?.questionsAsked || ["Were you with a group of people, or was it a solo/pair photo?", "Was this outdoors or indoors?"];
  const totalRounds = summary?.totalRounds || 2;

  const handleRating = (rating: number) => {
    setFeedbackRating(rating);
    onSubmitFeedback(rating);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Header */}
      <div style={{
        background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
        color: '#FFFFFF',
        padding: '20px',
        borderRadius: '16px',
        textAlign: 'center'
      }}>
        <h2 style={{ fontSize: '22px', fontWeight: 700, marginBottom: '4px' }}>
          Found it ✨
        </h2>
        <p style={{ fontSize: '13px', opacity: 0.9 }}>
          {totalRounds} questions • Target located
        </p>
      </div>

      {/* Target Image */}
      <div style={{
        background: '#FFFFFF',
        border: '1px solid #E2E8F0',
        borderRadius: '16px',
        overflow: 'hidden',
        boxShadow: '0 4px 12px rgba(0,0,0,0.06)'
      }}>
        <div style={{ aspectRatio: '4/3', width: '100%', background: '#F1F5F9' }}>
          <img
            src={targetPhoto.image_url}
            alt={targetPhoto.manual_label}
            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
            onError={(e) => {
              (e.target as HTMLImageElement).src = `https://picsum.photos/seed/${targetPhoto.image_id}/600/450`;
            }}
          />
        </div>
        <div style={{ padding: '16px' }}>
          <p style={{ fontSize: '13px', color: '#475569', fontStyle: 'italic', lineHeight: 1.4 }}>
            "{targetPhoto.manual_label}"
          </p>
        </div>
      </div>

      {/* How Memory Guide Found It - Retrieval Trace */}
      <div style={{
        background: 'linear-gradient(180deg, #F8FAFC 0%, #EFF6FF 100%)',
        border: '1px solid #BFDBFE',
        borderRadius: '16px',
        padding: '18px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
          <span style={{ fontSize: '16px' }}>✨</span>
          <h4 style={{ fontSize: '14px', fontWeight: 700, color: '#1E40AF' }}>
            How Memory Guide found it
          </h4>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '13px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#475569' }}>
            <span style={{ background: '#DBEAFE', color: '#1E40AF', padding: '2px 8px', borderRadius: '10px', fontWeight: 600, fontSize: '11px' }}>START</span>
            <span>29 photos in library</span>
          </div>

          <div style={{ color: '#94A3B8', paddingLeft: '14px', fontSize: '11px' }}>↓</div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#1E293B', fontWeight: 600 }}>
            <span style={{ background: '#E0F2FE', color: '#0369A1', padding: '2px 8px', borderRadius: '10px', fontSize: '11px' }}>QUERY</span>
            <span>12 possible photos</span>
          </div>

          {questionsAsked.map((q, idx) => (
            <React.Fragment key={idx}>
              <div style={{ color: '#94A3B8', paddingLeft: '14px', fontSize: '11px' }}>↓</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '2px', background: '#FFFFFF', padding: '8px 12px', borderRadius: '10px', border: '1px solid #E2E8F0' }}>
                <span style={{ fontSize: '11px', color: '#64748B', fontWeight: 500 }}>"{q}"</span>
                <span style={{ fontSize: '12px', color: '#1A73E8', fontWeight: 700 }}>
                  {idx === 0 ? '12 → 7 possible' : '7 → 4 possible'}
                </span>
              </div>
            </React.Fragment>
          ))}

          <div style={{ color: '#94A3B8', paddingLeft: '14px', fontSize: '11px' }}>↓</div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#065F46', background: '#D1FAE5', padding: '8px 12px', borderRadius: '10px', fontWeight: 700 }}>
            <span>Found ✓</span>
            <span style={{ fontSize: '11px', fontWeight: 500, color: '#047857' }}>(Target recognized)</span>
          </div>
        </div>
      </div>

      {/* Why did Memory Guide ask this? (Expandable) */}
      <div style={{ border: '1px solid #E2E8F0', borderRadius: '14px', overflow: 'hidden' }}>
        <button
          style={{
            width: '100%',
            padding: '12px 16px',
            background: '#F8FAFC',
            border: 'none',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            fontSize: '13px',
            fontWeight: 600,
            color: '#1E293B',
            cursor: 'pointer'
          }}
          onClick={() => setShowExplanation(!showExplanation)}
        >
          <span>Why did Memory Guide ask this?</span>
          <span>{showExplanation ? '▲' : '▼'}</span>
        </button>

        {showExplanation && (
          <div style={{ padding: '16px', fontSize: '13px', color: '#475569', lineHeight: 1.5, background: '#FFFFFF' }}>
            <p style={{ marginBottom: showDebug ? '12px' : 0 }}>
              Among the remaining photos, cake visibility and group/solo setting were the strongest features to separate candidate options cleanly.
            </p>
            {showDebug && selectionMetadata && (
              <div style={{
                background: '#F1F5F9',
                padding: '10px',
                borderRadius: '8px',
                fontFamily: 'monospace',
                fontSize: '11px',
                color: '#334155'
              }}>
                <div>Discrimination Score: {selectionMetadata.discriminationScore}</div>
                <div>Memorability Weight: {selectionMetadata.memorabilityWeight}</div>
                <div>Question Score: {selectionMetadata.finalScore}</div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Helpful feedback */}
      <div style={{ textAlign: 'center', padding: '10px' }}>
        <p style={{ fontSize: '12px', color: '#64748B', marginBottom: '8px' }}>
          Was this retrieval helpful?
        </p>
        <div style={{ display: 'flex', justifyContent: 'center', gap: '8px' }}>
          {[1, 2, 3, 4, 5].map((star) => (
            <button
              key={star}
              onClick={() => handleRating(star)}
              style={{
                background: feedbackRating && feedbackRating >= star ? '#FEF08A' : '#F1F5F9',
                border: '1px solid #E2E8F0',
                borderRadius: '8px',
                padding: '6px 12px',
                fontSize: '16px',
                cursor: 'pointer'
              }}
            >
              ★
            </button>
          ))}
        </div>
      </div>

      {/* Restart Actions */}
      <div style={{ display: 'flex', gap: '10px' }}>
        <button
          className="btn-primary"
          style={{ flex: 1, padding: '12px', borderRadius: '12px', justifyContent: 'center' }}
          onClick={onRestart}
        >
          Done
        </button>
        <button
          className="btn-secondary"
          style={{ flex: 1, padding: '12px', borderRadius: '12px', justifyContent: 'center' }}
          onClick={onRestart}
        >
          Find another photo
        </button>
      </div>
    </div>
  );
}
