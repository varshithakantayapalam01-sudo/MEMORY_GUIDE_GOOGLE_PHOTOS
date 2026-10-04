'use client';

import React from 'react';

interface NavbarProps {
  onActivateMemoryGuide: (query?: string) => void;
  onOpenResearchUpload: () => void;
  onReset: () => void;
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  isGuideActive: boolean;
}

export default function Navbar({
  onActivateMemoryGuide,
  onOpenResearchUpload,
  onReset,
  searchQuery,
  setSearchQuery,
  isGuideActive,
}: NavbarProps) {

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && searchQuery.trim()) {
      onActivateMemoryGuide(searchQuery.trim());
    }
  };

  return (
    <header className="gphotos-header">
      <div className="gphotos-header-left">
        <div className="gphotos-logo" onClick={onReset} style={{ cursor: 'pointer' }}>
          {/* Google Photos Pinwheel SVG Icon */}
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
            <path d="M12 2C12 6.42 8.42 10 4 10C8.42 10 12 13.58 12 18C12 13.58 15.58 10 20 10C15.58 10 12 6.42 12 2Z" fill="#EA4335"/>
            <path d="M2 12C6.42 12 10 8.42 10 4C10 8.42 13.58 12 18 12C13.58 12 10 15.58 10 20C10 15.58 6.42 12 2 12Z" fill="#4285F4"/>
            <path d="M12 22C12 17.58 15.58 14 20 14C15.58 14 12 10.42 12 6C12 10.42 8.42 14 4 14C8.42 14 12 17.58 12 22Z" fill="#FBBC05"/>
            <path d="M22 12C17.58 12 14 15.58 14 20C14 15.58 10.42 12 6 12C10.42 12 14 8.42 14 4C14 8.42 17.58 12 22 12Z" fill="#34A853"/>
          </svg>
          <span>Photos</span>
        </div>
        <span className="concept-badge">Google Photos • Core Experience Concept</span>
      </div>

      <div className="gphotos-search-container">
        <div style={{ position: 'relative', width: '100%' }}>
          <div className={`gphotos-search-bar ${isGuideActive ? 'active' : ''}`}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#5F6368" strokeWidth="2">
              <circle cx="11" cy="11" r="8"/>
              <line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            <input
              type="text"
              className="gphotos-search-input"
              placeholder="Search your photos"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              onFocus={() => {
                if (!isGuideActive) onActivateMemoryGuide();
              }}
            />
            <button
              type="button"
              className="memory-guide-chip-btn"
              onClick={() => onActivateMemoryGuide(searchQuery)}
            >
              <span>✨</span>
              <span>Memory Guide</span>
            </button>
          </div>
          <div style={{
            position: 'absolute',
            top: '50px',
            left: '16px',
            fontSize: '11px',
            color: '#1A73E8',
            fontWeight: 500,
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            whiteSpace: 'nowrap'
          }}>
            <span>✨</span>
            <span>Can't remember the exact words? Describe what you remember.</span>
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <button
          className="btn-secondary"
          onClick={onOpenResearchUpload}
          style={{ fontSize: '13px', padding: '6px 14px', borderRadius: '18px' }}
        >
          + Add your photos
        </button>
        <div
          style={{
            width: '36px',
            height: '36px',
            borderRadius: '50%',
            background: 'linear-gradient(135deg, #1A73E8, #34A853)',
            color: '#FFFFFF',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 600,
            fontSize: '14px',
          }}
        >
          P
        </div>
      </div>
    </header>
  );
}
