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
          <span className="mode-badge" style={{ marginBottom: '1rem', display: 'inline-block' }}>
            Guided Photo Retrieval Engine
          </span>
          <h1 className="title-main">
            Find the photo you remember — even when you can't describe it perfectly.
          </h1>
          <p className="subtitle">
            Tell Memory Guide what you remember. Instead of making you guess what to search next,
            it studies the remaining photos and asks the clue most likely to narrow them down.
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
