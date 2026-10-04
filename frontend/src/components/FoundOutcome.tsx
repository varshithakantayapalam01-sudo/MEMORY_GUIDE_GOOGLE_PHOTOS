'use client';

import { useState } from 'react';
import { FoundSummary } from '@/lib/api';

interface FoundOutcomeProps {
  selectedImageId?: string;
  summary?: FoundSummary;
  narrowingPathStr: string;
  onSubmitFeedback: (rating: number, confusingFeedback?: string) => Promise<void>;
  onRestart: () => void;
  loading: boolean;
}

export default function FoundOutcome({
  selectedImageId,
  summary,
  narrowingPathStr,
  onSubmitFeedback,
  onRestart,
  loading,
}: FoundOutcomeProps) {
  const [rating, setRating] = useState<number>(0);
  const [feedbackText, setFeedbackText] = useState('');
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);

  const handleFeedbackSubmit = async () => {
    if (rating > 0) {
      await onSubmitFeedback(rating, feedbackText);
      setFeedbackSubmitted(true);
    }
  };

  const pathDisplay = summary?.candidateNarrowingPath || narrowingPathStr;
  const questionsList = summary?.questionsAsked || [];

  return (
    <div className="card-container">
      <div className="found-banner">
        <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>🎉</div>
        <h2 className="found-title">Found it.</h2>
        <p style={{ color: 'var(--text-secondary)' }}>
          Memory Guide successfully narrowed down your target photo: <strong>{selectedImageId || 'Selected Photo'}</strong>
        </p>
      </div>

      {/* Retrieval Trace Summary */}
      <div className="summary-box">
        <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#ffffff', marginBottom: '0.75rem' }}>
          📍 Candidate Narrowing Path
        </h3>
        <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--accent-color)', marginBottom: '1rem' }}>
          {pathDisplay}
        </div>

        {questionsList.length > 0 && (
          <div style={{ textAlign: 'left', marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.5rem', fontWeight: 600 }}>
              Adaptive Questions Asked ({questionsList.length}):
            </p>
            <ol style={{ paddingLeft: '1.25rem', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
              {questionsList.map((q, idx) => (
                <li key={idx} style={{ marginBottom: '0.25rem' }}>{q}</li>
              ))}
            </ol>
          </div>
        )}
      </div>

      {/* Feedback Section */}
      {!feedbackSubmitted ? (
        <div style={{ textAlign: 'left', background: 'var(--bg-card)', padding: '1.5rem', borderRadius: 'var(--radius-md)', marginBottom: '2rem' }}>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: '#ffffff', marginBottom: '0.5rem' }}>
            Did the questions help you remember or communicate useful details?
          </h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>
            Rate your experience (1 = Not helpful, 5 = Very helpful)
          </p>

          <div className="rating-group">
            {[1, 2, 3, 4, 5].map((star) => (
              <button
                key={star}
                type="button"
                className={`star-btn ${rating >= star ? 'selected' : ''}`}
                onClick={() => setRating(star)}
              >
                {star}
              </button>
            ))}
          </div>

          <div style={{ marginTop: '1rem' }}>
            <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>
              What, if anything, felt confusing or unhelpful? (Optional)
            </label>
            <textarea
              className="input-textarea"
              style={{ minHeight: '80px', marginBottom: '1rem' }}
              placeholder="e.g. Question 2 was a bit too specific..."
              value={feedbackText}
              onChange={(e) => setFeedbackText(e.target.value)}
            />

            <button
              className="btn-primary"
              onClick={handleFeedbackSubmit}
              disabled={loading || rating === 0}
              style={{ padding: '0.65rem 1.25rem', fontSize: '0.9rem' }}
            >
              {loading ? <span className="spinner" /> : 'Submit Feedback'}
            </button>
          </div>
        </div>
      ) : (
        <div style={{ background: 'var(--success-bg)', border: '1px solid var(--success-color)', padding: '1rem', borderRadius: '8px', marginBottom: '2rem' }}>
          <p style={{ color: 'var(--success-color)', fontWeight: 600 }}>Thank you for your feedback! 🙏</p>
        </div>
      )}

      <div>
        <button className="btn-secondary" onClick={onRestart} style={{ width: '100%' }}>
          🔄 Start Another Search
        </button>
      </div>
    </div>
  );
}
