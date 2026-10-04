'use client';

interface NavbarProps {
  mode: 'demo' | 'research' | null;
  onReset: () => void;
  showDebug: boolean;
  onToggleDebug: () => void;
}

export default function Navbar({ mode, onReset, showDebug, onToggleDebug }: NavbarProps) {
  return (
    <header className="app-header">
      <div className="logo-group" onClick={onReset} style={{ cursor: 'pointer' }}>
        <div className="logo-icon">M</div>
        <div style={{ display: 'flex', flexDirection: 'column', textAlign: 'left' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span>Memory Guide</span>
            {mode && <span className="mode-badge">{mode.toUpperCase()} MODE</span>}
          </div>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 500 }}>
            Google Photos • Core Experience Concept
          </span>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
        <button
          className="btn-ghost"
          onClick={onToggleDebug}
          title="Toggle research debug metrics"
          style={{ fontSize: '0.8rem', opacity: showDebug ? 1 : 0.6 }}
        >
          {showDebug ? '🐛 Debug ON' : '🐛 Debug OFF'}
        </button>
        {mode && (
          <button className="btn-secondary" onClick={onReset} style={{ padding: '0.4rem 0.85rem', fontSize: '0.85rem' }}>
            New Search
          </button>
        )}
      </div>
    </header>
  );
}
