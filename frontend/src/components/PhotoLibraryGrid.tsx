'use client';

import React, { useState } from 'react';
import { DEMO_PHOTOS, DemoPhoto } from '@/lib/demoFallbackEngine';

interface PhotoLibraryGridProps {
  activeCandidateIds?: string[];
  isGuideActive?: boolean;
  mode?: 'demo' | 'research';
  uploadedCount?: number;
}

export default function PhotoLibraryGrid({ activeCandidateIds, isGuideActive, mode = 'demo', uploadedCount = 0 }: PhotoLibraryGridProps) {
  const [failedImageIds, setFailedImageIds] = useState<Record<string, boolean>>({});

  // Group photos loosely by date/month as required
  const oct2025 = DEMO_PHOTOS.filter(p => p.cluster_id === 'birthday');
  const aug2025 = DEMO_PHOTOS.filter(p => p.cluster_id === 'vacation');
  const summer2025 = DEMO_PHOTOS.filter(p => p.cluster_id === 'outdoor');
  const earlier = DEMO_PHOTOS.filter(p => p.cluster_id === 'celebration');

  // Candidate dimming ONLY activates after user submits a query AND has active candidates
  const hasCandidateFilter = Boolean(isGuideActive && activeCandidateIds && activeCandidateIds.length > 0);

  if (mode === 'research') {
    return (
      <div className="gphotos-content">
        <div style={{
          background: 'linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%)',
          border: '1px solid #BAE6FD',
          borderRadius: '16px',
          padding: '32px 24px',
          maxWidth: '600px',
          margin: '30px auto',
          textAlign: 'center',
          boxShadow: '0 4px 16px rgba(0,0,0,0.04)'
        }}>
          <div style={{ fontSize: '40px', marginBottom: '12px' }}>📷🔒</div>
          <h3 style={{ fontSize: '20px', fontWeight: 700, color: '#0F172A', marginBottom: '8px' }}>
            Research Session Library Ready
          </h3>
          <p style={{ fontSize: '14px', color: '#475569', lineHeight: 1.6, marginBottom: '20px' }}>
            {uploadedCount > 0 ? `${uploadedCount} uploaded photos` : 'Your uploaded photos'} are indexed for this research retrieval session.
            <br />
            Photos are hidden during memory tasks to prevent pre-task visual exposure.
          </p>
          {hasCandidateFilter ? (
            <div style={{
              background: '#10B981',
              color: '#FFFFFF',
              padding: '10px 18px',
              borderRadius: '12px',
              fontSize: '13px',
              fontWeight: 600,
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <span>✨</span>
              <span>Memory Guide Active — Evaluating {activeCandidateIds?.length || 0} candidate photo{(activeCandidateIds?.length || 0) === 1 ? '' : 's'}</span>
            </div>
          ) : (
            <div style={{
              background: '#E2E8F0',
              color: '#475569',
              padding: '8px 14px',
              borderRadius: '12px',
              fontSize: '12px',
              fontWeight: 500,
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              <span>✨ Click "Memory Guide AI" to start searching your photos</span>
            </div>
          )}
        </div>
      </div>
    );
  }

  const renderPhotoTile = (photo: DemoPhoto) => {
    const isCandidate = activeCandidateIds?.includes(photo.image_id);
    const isFailed = failedImageIds[photo.image_id];

    const tileStyle: React.CSSProperties = {
      position: 'relative',
      aspectRatio: '1 / 1',
      borderRadius: '8px',
      overflow: 'hidden',
      backgroundColor: '#F1F3F4',
      cursor: 'pointer',
      transition: 'opacity 0.25s ease, box-shadow 0.25s ease, transform 0.15s ease',
      opacity: !hasCandidateFilter || isCandidate ? 1 : 0.35,
      filter: hasCandidateFilter && !isCandidate ? 'grayscale(20%)' : 'none',
      boxShadow: hasCandidateFilter && isCandidate ? '0 0 0 3px #1A73E8' : 'none',
    };

    if (isFailed) {
      return (
        <div key={photo.image_id} style={tileStyle}>
          <div style={{
            width: '100%',
            height: '100%',
            background: '#F1F5F9',
            color: '#64748B',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '12px',
            textAlign: 'center',
            padding: '8px'
          }}>
            <span style={{ fontSize: '20px', marginBottom: '4px' }}>🖼️</span>
            <span>Photo unavailable</span>
          </div>
        </div>
      );
    }

    return (
      <div key={photo.image_id} className="photo-tile" style={tileStyle}>
        <img
          src={photo.image_url}
          alt={photo.manual_label}
          loading="lazy"
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            display: 'block',
            opacity: 1,
            filter: 'none',
          }}
          onError={() => {
            setFailedImageIds(prev => ({ ...prev, [photo.image_id]: true }));
          }}
        />
      </div>
    );
  };

  return (
    <div className="gphotos-content">
      {hasCandidateFilter && (
        <div style={{
          background: '#E8F0FE',
          color: '#1A73E8',
          padding: '10px 16px',
          borderRadius: '12px',
          marginBottom: '20px',
          fontSize: '13px',
          fontWeight: '500',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <span>✨</span>
          <span>Memory Guide active — showing {activeCandidateIds?.length || 0} candidate photo{(activeCandidateIds?.length || 0) === 1 ? '' : 's'} highlighted in your library</span>
        </div>
      )}

      <div>
        <div className="library-section-title">October 2025</div>
        <div className="photos-grid">
          {oct2025.map(renderPhotoTile)}
        </div>
      </div>

      <div>
        <div className="library-section-title">August 2025</div>
        <div className="photos-grid">
          {aug2025.map(renderPhotoTile)}
        </div>
      </div>

      <div>
        <div className="library-section-title">Summer 2025</div>
        <div className="photos-grid">
          {summer2025.map(renderPhotoTile)}
        </div>
      </div>

      <div>
        <div className="library-section-title">Earlier</div>
        <div className="photos-grid">
          {earlier.map(renderPhotoTile)}
        </div>
      </div>
    </div>
  );
}
