'use client';

import React, { useState } from 'react';

interface ResearchUploadViewProps {
  onUpload: (files: File[]) => Promise<void>;
  onProceedToQuery: () => void;
  onClose: () => void;
  loading: boolean;
  uploadStatus: 'idle' | 'uploading' | 'ready' | 'error';
  imageCount: number;
  errorMessage?: string;
}

export default function ResearchUploadView({
  onUpload,
  onProceedToQuery,
  onClose,
  loading,
  uploadStatus,
  imageCount,
  errorMessage,
}: ResearchUploadViewProps) {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const filesArr = Array.from(e.target.files).slice(0, 30);
      setSelectedFiles(filesArr);
    }
  };

  const handleStartUpload = async () => {
    if (selectedFiles.length > 0) {
      await onUpload(selectedFiles);
    }
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0,0,0,0.4)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 200,
      padding: '20px'
    }}>
      <div style={{
        background: '#FFFFFF',
        borderRadius: '20px',
        padding: '28px',
        maxWidth: '480px',
        width: '100%',
        boxShadow: '0 8px 32px rgba(0,0,0,0.15)',
        display: 'flex',
        flexDirection: 'column',
        gap: '20px'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 style={{ fontSize: '18px', fontWeight: 700, color: '#1E293B' }}>
            Add Your Photos
          </h3>
          <button className="btn-ghost" onClick={onClose}>✕</button>
        </div>

        <p style={{ fontSize: '13px', color: '#64748B', lineHeight: 1.5 }}>
          Upload up to 30 of your personal photos to test Memory Guide AI retrieval on your own library.
        </p>

        {uploadStatus === 'idle' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <label style={{
              border: '2px dashed #CBD5E1',
              borderRadius: '16px',
              padding: '24px',
              textAlign: 'center',
              cursor: 'pointer',
              background: '#F8FAFC'
            }}>
              <input
                type="file"
                multiple
                accept="image/*"
                onChange={handleFileChange}
                style={{ display: 'none' }}
              />
              <div style={{ fontSize: '28px', marginBottom: '8px' }}>📷</div>
              <div style={{ fontSize: '14px', fontWeight: 600, color: '#1A73E8' }}>
                {selectedFiles.length > 0 ? `${selectedFiles.length} photos selected` : 'Select up to 30 photos'}
              </div>
              <div style={{ fontSize: '12px', color: '#94A3B8', marginTop: '4px' }}>
                JPG, PNG, WebP supported
              </div>
            </label>

            {selectedFiles.length > 0 && (
              <button
                className="btn-primary"
                style={{ width: '100%', padding: '12px', borderRadius: '12px', justifyContent: 'center' }}
                onClick={handleStartUpload}
                disabled={loading}
              >
                Upload & Process Library
              </button>
            )}
          </div>
        )}

        {uploadStatus === 'uploading' && (
          <div style={{ textAlign: 'center', padding: '24px 0' }}>
            <div style={{
              width: '32px',
              height: '32px',
              border: '3px solid #CBD5E1',
              borderTopColor: '#1A73E8',
              borderRadius: '50%',
              animation: 'spin 0.8s linear infinite',
              margin: '0 auto 12px auto'
            }} />
            <h4 style={{ fontSize: '15px', fontWeight: 600, color: '#1E293B' }}>
              Preparing your library…
            </h4>
            <p style={{ fontSize: '12px', color: '#64748B', marginTop: '4px' }}>
              Extracting candidate features & vector embeddings
            </p>
          </div>
        )}

        {uploadStatus === 'ready' && (
          <div style={{ textAlign: 'center', padding: '16px 0', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div style={{ fontSize: '36px' }}>✅</div>
            <div>
              <h4 style={{ fontSize: '16px', fontWeight: 700, color: '#1E293B' }}>
                Your photos are ready.
              </h4>
              <p style={{ fontSize: '13px', color: '#64748B', marginTop: '4px' }}>
                {imageCount} photos added to your memory guide session.
              </p>
            </div>
            <button
              className="btn-primary"
              style={{ width: '100%', padding: '12px', borderRadius: '12px', justifyContent: 'center' }}
              onClick={() => {
                onProceedToQuery();
                onClose();
              }}
            >
              Start Memory Guide AI Search
            </button>
          </div>
        )}

        {errorMessage && (
          <div style={{ color: '#DC2626', fontSize: '12px', background: '#FEF2F2', padding: '10px', borderRadius: '8px' }}>
            ⚠️ {errorMessage}
          </div>
        )}
      </div>
    </div>
  );
}
