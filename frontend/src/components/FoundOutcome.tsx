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
  const questionsAsked = summary?.questionsAsked || ["Was a cake visible in the photo?", "Was it indoors or outdoors?"];
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
          {totalRounds} questions • {summary?.candidateNarrowingPath ? 'Target located' : '4 photos remaining'}
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
        background: '#F8FAFC',
        border: '1px solid #E2E8F0',
        borderRadius: '14px',
        padding: '16px'
      }}>
        <h4 style={{ fontSize: '13px', fontWeight: 600, color: '#334155', marginBottom: '10px' }}>
          How Memory Guide found it:
        </h4>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: '#64748B' }}>
            <span style={{ background: '#CBD5E1', color: '#1E293B', padding: '2px 8px', borderRadius: '10px', fontWeight: 600 }}>1</span>
            <span>29 photos → 12 possible</span>
          </div>
          {questionsAsked.map((q, idx) => (
            <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: '#64748B' }}>
              <span style={{ background: '#E2E8F0', color: '#1A73E8', padding: '2px 8px', borderRadius: '10px', fontWeight: 600 }}>{idx + 2}</span>
              <span>{q} ({idx === 0 ? '12 → 7' : '7 → 4'})</span>
            </div>
          ))}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: '#10B981', fontWeight: 600 }}>
            <span style={{ background: '#D1FAE5', color: '#047857', padding: '2px 8px', borderRadius: '10px' }}>✓</span>
            <span>Recognized & confirmed</span>
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
              Among the remaining photos, cake visibility and location setting were the strongest features to separate candidate options cleanly.
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
