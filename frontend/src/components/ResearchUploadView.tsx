'use client';

import { useState, ChangeEvent } from 'react';

interface ResearchUploadViewProps {
  onUpload: (files: File[]) => Promise<void>;
  onProceedToQuery: () => void;
  loading: boolean;
  uploadStatus: 'idle' | 'uploading' | 'ready' | 'error';
  imageCount: number;
  errorMessage?: string;
}

export default function ResearchUploadView({
  onUpload,
  onProceedToQuery,
  loading,
  uploadStatus,
  imageCount,
  errorMessage,
}: ResearchUploadViewProps) {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files).slice(0, 30);
      setSelectedFiles(files);
    }
  };

  const handleStartUpload = async () => {
    if (selectedFiles.length > 0) {
      await onUpload(selectedFiles);
    }
  };

  return (
    <div className="card-container">
      <h2 className="section-title">Use My Photos</h2>
      <p className="subtitle">
        Upload up to 30 photos from your personal collection to search using Memory Guide.
      </p>

      {uploadStatus === 'idle' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', alignItems: 'flex-start' }}>
          <input
            type="file"
            multiple
            accept="image/*"
            onChange={handleFileChange}
            id="photo-file-input"
            style={{ display: 'none' }}
          />
          <label
            htmlFor="photo-file-input"
            className="btn-secondary"
            style={{ cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}
          >
            📁 Select Photos ({selectedFiles.length} selected)
          </label>

          {selectedFiles.length > 0 && (
            <div>
              <p style={{ color: 'var(--text-secondary)', marginBottom: '1rem', fontSize: '0.9rem' }}>
                {selectedFiles.length} photo(s) selected and ready for upload.
              </p>
              <button
                className="btn-primary"
                onClick={handleStartUpload}
                disabled={loading}
              >
                {loading ? <span className="spinner" /> : 'Upload & Index Photos'}
              </button>
            </div>
          )}
        </div>
      )}

      {uploadStatus === 'uploading' && (
        <div className="loading-container">
          <div className="spinner" style={{ width: 36, height: 36 }} />
          <p className="loading-text">Preparing your photos…</p>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
            Extracting memory features and preparing indexing pool.
          </p>
        </div>
      )}

      {uploadStatus === 'ready' && (
        <div style={{ textAlign: 'center', padding: '1.5rem 0' }}>
          <div
            style={{
              width: 56,
              height: 56,
              borderRadius: '50%',
              background: 'var(--success-bg)',
              color: 'var(--success-color)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1.75rem',
              margin: '0 auto 1rem auto',
            }}
          >
            ✓
          </div>
          <h3 style={{ fontSize: '1.5rem', color: '#ffffff', marginBottom: '0.5rem' }}>
            Your photos are ready.
          </h3>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
            {imageCount} photo(s) indexed in your private session.
          </p>
          <button className="btn-primary" onClick={onProceedToQuery}>
            Continue to Memory Input →
          </button>
        </div>
      )}

      {uploadStatus === 'error' && (
        <div style={{ background: 'rgba(248, 113, 113, 0.1)', border: '1px solid var(--danger-color)', padding: '1rem', borderRadius: '8px', marginTop: '1rem' }}>
          <p style={{ color: 'var(--danger-color)', fontWeight: 600 }}>Upload Error</p>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>{errorMessage || 'Failed to upload photos. Please try again.'}</p>
        </div>
      )}
    </div>
  );
}
