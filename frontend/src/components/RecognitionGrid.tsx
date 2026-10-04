'use client';

import { CandidateData } from '@/lib/api';

interface RecognitionGridProps {
  candidates: CandidateData[];
  onSelectFound: (imageId: string) => Promise<void>;
  onSelectClose: (imageId: string) => Promise<void>;
  onSelectNone: () => Promise<void>;
  loading: boolean;
}

const getFullImageUrl = (url: string) => {
  if (!url) return '';
  if (url.startsWith('http://') || url.startsWith('https://') || url.startsWith('data:')) {
    return url;
  }
  const apiBase = process.env.NEXT_PUBLIC_API_URL || 'https://memoryguidegooglephotos-production.up.railway.app/api/v1';
  const origin = apiBase.replace(/\/api\/v1\/?$/, '');
  return `${origin}${url.startsWith('/') ? '' : '/'}${url}`;
};

export default function RecognitionGrid({
  candidates,
  onSelectFound,
  onSelectClose,
  onSelectNone,
  loading,
}: RecognitionGridProps) {
  return (
    <div className="card-container" style={{ maxWidth: '900px' }}>
      <div className="recognition-header">
        <h2 className="section-title">Is one of these the photo you remember?</h2>
        <p className="subtitle" style={{ margin: '0 auto 1.5rem auto' }}>
          Select the matching photo, choose one that looks close as a reference, or let Memory Guide keep searching.
        </p>
      </div>

      {loading && (
        <div className="loading-container" style={{ marginBottom: '1.5rem' }}>
          <div className="spinner" />
          <p className="loading-text">Finding the closest matches…</p>
        </div>
      )}

      <div className="photo-grid">
        {candidates.map((cand, idx) => (
          <div key={cand.imageId} className="photo-card" id={`photo-card-${cand.imageId}`}>
            <div className="photo-img-wrapper">
              <img
                src={getFullImageUrl(cand.imageUrl)}
                alt={`Candidate photo ${idx + 1}`}
                className="photo-img"
                onError={(e) => {
                  // Fallback for broken images or demo paths
                  const target = e.target as HTMLImageElement;
                  target.style.display = 'none';
                  const parent = target.parentElement;
                  if (parent) {
                    const fallback = document.createElement('div');
                    fallback.className = 'photo-fallback';
                    fallback.innerHTML = `<span>📷 Candidate Photo #${idx + 1}</span><span style="font-size:0.75rem;opacity:0.7;">(${cand.imageId})</span>`;
                    parent.appendChild(fallback);
                  }
                }}
              />
            </div>

            <div className="photo-body">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                  Photo #{idx + 1}
                </span>
                <span
                  style={{
                    fontSize: '0.75rem',
                    background: 'var(--accent-glow)',
                    color: 'var(--accent-color)',
                    padding: '0.15rem 0.5rem',
                    borderRadius: '4px',
                    fontWeight: 600,
                  }}
                >
                  Score: {(cand.score * 100).toFixed(0)}%
                </span>
              </div>

              <div className="photo-actions">
                <button
                  className="btn-card-found"
                  onClick={() => onSelectFound(cand.imageId)}
                  disabled={loading}
                  id={`select-found-${cand.imageId}`}
                >
                  ✓ This is it
                </button>
                <button
                  className="btn-card-close"
                  onClick={() => onSelectClose(cand.imageId)}
                  disabled={loading}
                  id={`select-close-${cand.imageId}`}
                >
                  🔍 This looks close
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="none-bar">
        <button
          className="btn-secondary"
          onClick={onSelectNone}
          disabled={loading}
          style={{ width: '100%', maxWidth: '320px', padding: '0.85rem 1.5rem' }}
          id="select-none-btn"
        >
          ❌ None of these
        </button>
      </div>
    </div>
  );
}
