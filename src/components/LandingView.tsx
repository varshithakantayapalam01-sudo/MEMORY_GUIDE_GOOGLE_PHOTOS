'use client';

interface LandingViewProps {
  onStartDemo: () => void;
  onStartResearch: () => void;
  loading: boolean;
}

export default function LandingView({ onStartDemo, onStartResearch, loading }: LandingViewProps) {
  return (
    <div className="card-container">
      <div className="hero-grid">
        <div>
          <div style={{ fontSize: '0.85rem', color: '#94a3b8', fontWeight: 600, marginBottom: '0.5rem', letterSpacing: '0.02em' }}>
            Google Photos • Core Experience Concept
          </div>
          <span className="mode-badge" style={{ marginBottom: '1rem', display: 'inline-block' }}>
            Guided Photo Retrieval Engine
          </span>
          <h1 className="title-main">
            Find the photo you remember — even when you can't describe it perfectly.
          </h1>
          <p className="subtitle">
            Google Photos holds thousands of memories, but vague queries often fail. Tell Memory Guide what you remember.
            Instead of making you guess keywords, it analyzes candidate photos and asks adaptive questions to narrow them down.
          </p>

          <div className="hero-actions">
            <button
              className="btn-primary"
              onClick={onStartDemo}
              disabled={loading}
              id="try-demo-btn"
            >
              {loading ? <span className="spinner" /> : '✨ Try Demo'}
            </button>
            <button
              className="btn-secondary"
              onClick={onStartResearch}
              disabled={loading}
              id="use-my-photos-btn"
            >
              📷 Use My Photos
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
