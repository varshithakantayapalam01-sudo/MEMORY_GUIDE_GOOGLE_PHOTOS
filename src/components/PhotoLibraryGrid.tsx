'use client';

import React, { useState } from 'react';
import { DEMO_PHOTOS, DemoPhoto } from '@/lib/demoFallbackEngine';

interface PhotoLibraryGridProps {
  activeCandidateIds?: string[];
  isGuideActive?: boolean;
}

export default function PhotoLibraryGrid({ activeCandidateIds, isGuideActive }: PhotoLibraryGridProps) {
  const [failedImageIds, setFailedImageIds] = useState<Record<string, boolean>>({});

  // Group photos loosely by date/month as required
  const oct2025 = DEMO_PHOTOS.filter(p => p.cluster_id === 'birthday');
  const aug2025 = DEMO_PHOTOS.filter(p => p.cluster_id === 'vacation');
  const summer2025 = DEMO_PHOTOS.filter(p => p.cluster_id === 'outdoor');
  const earlier = DEMO_PHOTOS.filter(p => p.cluster_id === 'celebration');

  // Candidate dimming ONLY activates after user submits a query AND has active candidates
  const hasCandidateFilter = Boolean(isGuideActive && activeCandidateIds && activeCandidateIds.length > 0);

  const renderPhotoTile = (photo: DemoPhoto) => {
    const isCandidate = activeCandidateIds?.includes(photo.image_id);
    const isFailed = failedImageIds[photo.image_id];

    // Candidate dimming rule:
    // If no candidate filter is active: opacity 1
    // If photo is in candidate pool: opacity 1, active border
    // Otherwise: soft fade (0.35 opacity), NEVER pure black
    const tileStyle: React.CSSProperties = {
      position: 'relative',
      aspectRatio: '1 / 1',
      borderRadius: '8px',
      overflow: 'hidden',
      backgroundColor: '#F1F3F4', // Light neutral background, NOT black
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
