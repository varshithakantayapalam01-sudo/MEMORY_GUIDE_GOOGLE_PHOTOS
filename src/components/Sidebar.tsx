'use client';

import React from 'react';

interface SidebarProps {
  activeTab: 'photos' | 'memories' | 'search' | 'collections';
  setActiveTab: (tab: 'photos' | 'memories' | 'search' | 'collections') => void;
  onActivateMemoryGuide: () => void;
}

export default function Sidebar({ activeTab, setActiveTab, onActivateMemoryGuide }: SidebarProps) {
  return (
    <aside className="gphotos-sidebar">
      <div
        className={`sidebar-nav-item ${activeTab === 'photos' ? 'active' : ''}`}
        onClick={() => setActiveTab('photos')}
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
          <path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/>
        </svg>
        <span>Photos</span>
      </div>

      <div
        className={`sidebar-nav-item ${activeTab === 'memories' ? 'active' : ''}`}
        onClick={() => setActiveTab('memories')}
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
        </svg>
        <span>Memories</span>
      </div>

      <div
        className={`sidebar-nav-item ${activeTab === 'search' ? 'active' : ''}`}
        onClick={() => {
          setActiveTab('search');
          onActivateMemoryGuide();
        }}
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
          <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
        </svg>
        <span>Search</span>
      </div>

      <div
        className={`sidebar-nav-item ${activeTab === 'collections' ? 'active' : ''}`}
        onClick={() => setActiveTab('collections')}
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
          <path d="M4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm16-4H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H8V4h12v12z"/>
        </svg>
        <span>Collections</span>
      </div>
    </aside>
  );
}
