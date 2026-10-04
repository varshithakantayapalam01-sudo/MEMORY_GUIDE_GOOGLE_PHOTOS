'use client';

import React from 'react';
import { DEMO_PHOTOS, DemoPhoto } from '@/lib/demoFallbackEngine';

interface PhotoLibraryGridProps {
  activeCandidateIds?: string[];
  isGuideActive?: boolean;
}

export default function PhotoLibraryGrid({ activeCandidateIds, isGuideActive }: PhotoLibraryGridProps) {
  // Group photos loosely by date/month as required
  const oct2025 = DEMO_PHOTOS.filter(p => p.cluster_id === 'birthday');
  const aug2025 = DEMO_PHOTOS.filter(p => p.cluster_id === 'vacation');
  const summer2025 = DEMO_PHOTOS.filter(p => p.cluster_id === 'outdoor');
  const earlier = DEMO_PHOTOS.filter(p => p.cluster_id === 'celebration');

  const hasCandidateFilter = isGuideActive && activeCandidateIds && activeCandidateIds.length > 0;

  const renderPhotoTile = (photo: DemoPhoto) => {
    const isCandidate = activeCandidateIds?.includes(photo.image_id);
    const tileClass = hasCandidateFilter
      ? isCandidate
        ? 'photo-tile candidate-active'
        : 'photo-tile dimmed'
      : 'photo-tile';

    return (
      <div key={photo.image_id} className={tileClass}>
        <img
          src={photo.image_url}
          alt={photo.manual_label}
          loading="lazy"
          onError={(e) => {
            // Fallback placeholder image if local image missing
            (e.target as HTMLImageElement).src = `https://picsum.photos/seed/${photo.image_id}/400/400`;
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
          <span>Memory Guide active — showing {activeCandidateIds.length} candidate photo{activeCandidateIds.length === 1 ? '' : 's'} highlighted in your library</span>
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
