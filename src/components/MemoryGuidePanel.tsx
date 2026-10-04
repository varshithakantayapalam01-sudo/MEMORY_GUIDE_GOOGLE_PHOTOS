'use client';

import React, { useState } from 'react';
import QuestionCard from './QuestionCard';
import RecognitionGrid from './RecognitionGrid';
import FoundOutcome from './FoundOutcome';
import {
  QuestionData,
  ProgressData,
  CandidateData,
  FoundSummary,
  SelectionMetadata
} from '@/lib/api';

interface MemoryGuidePanelProps {
  step: 'memory_input' | 'question' | 'recognition' | 'found';
  onClose: () => void;
  onSubmitQuery: (query: string) => Promise<void>;
  currentQuestion?: QuestionData;
  progress?: ProgressData;
  narrowingHistory: number[];
  confirmedClues: string[];
  onAnswerQuestion: (answerText: string) => Promise<void>;
  candidates: CandidateData[];
  onSelectFound: (imageId: string) => Promise<void>;
  onSelectClose: (imageId: string) => Promise<void>;
  onSelectNone: () => Promise<void>;
  foundSummary?: FoundSummary;
  selectedImageId?: string;
  narrowingPathStr: string;
  onSubmitFeedback: (rating: number, confusingFeedback?: string) => Promise<void>;
  onRestart: () => void;
  loading: boolean;
  referenceBanner?: string | null;
  selectionMetadata?: SelectionMetadata;
  showDebug: boolean;
  onToggleDebug: () => void;
  mode?: 'demo' | 'research';
  uploadedCount?: number;
  sessionId?: string | null;
}

export default function MemoryGuidePanel({
  step,
  onClose,
  onSubmitQuery,
  currentQuestion,
  progress,
  narrowingHistory,
  confirmedClues,
  onAnswerQuestion,
  candidates,
  onSelectFound,
  onSelectClose,
  onSelectNone,
  foundSummary,
  selectedImageId,
  narrowingPathStr,
  onSubmitFeedback,
  onRestart,
  loading,
  referenceBanner,
  selectionMetadata,
  showDebug,
  onToggleDebug,
  mode = 'demo',
  uploadedCount = 0,
  sessionId,
}: MemoryGuidePanelProps) {
  const [queryInput, setQueryInput] = useState('');

  const handleQuerySubmit = (queryToSubmit?: string) => {
    const text = queryToSubmit || queryInput;
    if (text.trim()) {
      onSubmitQuery(text.trim());
    }
  };

  return (
    <aside className="memory-guide-panel">
      {/* Panel Header */}
      <div className="panel-header">
        <div>
          <div className="panel-title">
            <span>✨</span>
            <span>Memory Guide</span>
          </div>
          {mode === 'research' ? (
            <div style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              background: '#E6F4EA',
              color: '#137333',
              fontSize: '12px',
              fontWeight: 600,
              padding: '4px 10px',
              borderRadius: '12px',
              marginTop: '6px'
            }}>
              <span>📷</span>
              <span>Searching your uploaded library • {uploadedCount} photos</span>
            </div>
          ) : (
            <p className="panel-subtext">
              Tell me what you remember. I'll figure out which clue would help narrow it down.
            </p>
          )}
        </div>
        <button className="btn-ghost" onClick={onClose} style={{ fontSize: '18px', padding: '4px 8px' }}>
          ✕
        </button>
      </div>

      {/* Panel Body */}
      <div className="panel-body">
        {step === 'memory_input' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <label style={{ fontSize: '13px', fontWeight: 600, color: '#334155' }}>
                Describe the photo you remember…
              </label>
              <textarea
                style={{
                  width: '100%',
                  height: '90px',
                  padding: '12px 14px',
                  borderRadius: '12px',
                  border: '1px solid #CBD5E1',
                  fontSize: '14px',
                  fontFamily: 'inherit',
                  outline: 'none',
                  resize: 'none'
                }}
                placeholder="That birthday picture from years ago…"
                value={queryInput}
                onChange={(e) => setQueryInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleQuerySubmit();
                  }
                }}
              />
              <span style={{ fontSize: '11px', color: '#64748B' }}>
                You don't need the exact date or keywords.
              </span>
            </div>

            <button
              className="btn-primary"
              style={{ width: '100%', padding: '12px', borderRadius: '12px', justifyContent: 'center' }}
              onClick={() => handleQuerySubmit()}
              disabled={loading || !queryInput.trim()}
            >
              {loading ? 'Looking through your library…' : 'Find photo'}
            </button>

            {/* Suggestion chips */}
            <div style={{ marginTop: '8px' }}>
              <div style={{ fontSize: '12px', fontWeight: 600, color: '#64748B', marginBottom: '8px' }}>
                Try an example memory:
              </div>
              <div className="chip-container">
                <button
                  className="suggestion-chip"
                  onClick={() => {
                    setQueryInput("That birthday picture from years ago");
                    handleQuerySubmit("That birthday picture from years ago");
                  }}
                >
                  "That birthday picture from years ago"
                </button>
                <button
                  className="suggestion-chip"
                  onClick={() => {
                    setQueryInput("That beach photo where I was with people");
                    handleQuerySubmit("That beach photo where I was with people");
                  }}
                >
                  "That beach photo where I was with people"
                </button>
                <button
                  className="suggestion-chip"
                  onClick={() => {
                    setQueryInput("That festival photo where we were dressed traditionally");
                    handleQuerySubmit("That festival photo where we were dressed traditionally");
                  }}
                >
                  "That festival photo where we were dressed traditionally"
                </button>
              </div>
            </div>

            {loading && (
              <div style={{
                background: '#F8FAFC',
                border: '1px solid #E2E8F0',
                padding: '14px',
                borderRadius: '12px',
                fontSize: '13px',
                color: '#1A73E8',
                display: 'flex',
                alignItems: 'center',
                gap: '10px'
              }}>
                <div style={{
                  width: '16px',
                  height: '16px',
                  border: '2px solid #93C5FD',
                  borderTopColor: '#1A73E8',
                  borderRadius: '50%',
                  animation: 'spin 0.8s linear infinite'
                }} />
                <span>
                  {mode === 'research'
                    ? `Looking through your library… (${uploadedCount} photos)`
                    : 'Looking through your library… (29 photos → 12 possible)'}
                </span>
              </div>
            )}
          </div>
        )}

        {step === 'question' && currentQuestion && (
          <QuestionCard
            question={currentQuestion}
            progress={progress}
            narrowingHistory={narrowingHistory}
            confirmedClues={confirmedClues}
            onAnswer={onAnswerQuestion}
            loading={loading}
            referenceBanner={referenceBanner}
          />
        )}

        {step === 'recognition' && (
          <RecognitionGrid
            candidates={candidates}
            onSelectFound={onSelectFound}
            onSelectClose={onSelectClose}
            onSelectNone={onSelectNone}
            loading={loading}
          />
        )}

        {step === 'found' && (
          <FoundOutcome
            selectedImageId={selectedImageId}
            summary={foundSummary}
            narrowingPathStr={narrowingPathStr}
            onSubmitFeedback={onSubmitFeedback}
            onRestart={onRestart}
            loading={loading}
            selectionMetadata={selectionMetadata}
            showDebug={showDebug}
            mode={mode}
            uploadedCount={uploadedCount}
            sessionId={sessionId}
            candidates={candidates}
          />
        )}
      </div>

      {/* Debug Trace Toggle Footer */}
      <div style={{
        marginTop: 'auto',
        padding: '12px 24px',
        borderTop: '1px solid #F0F0F0',
        background: '#F8FAFC',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <span style={{ fontSize: '11px', color: '#94A3B8' }}>AI Retrieval Strategy</span>
        <button
          className="btn-ghost"
          style={{ fontSize: '11px', padding: '2px 6px' }}
          onClick={onToggleDebug}
        >
          {showDebug ? 'Hide Debug' : 'Show Debug'}
        </button>
      </div>
    </aside>
  );
}
