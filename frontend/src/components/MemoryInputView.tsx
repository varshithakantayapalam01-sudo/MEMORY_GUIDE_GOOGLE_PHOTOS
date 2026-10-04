'use client';

import { useState, FormEvent } from 'react';

interface MemoryInputViewProps {
  onSubmitQuery: (query: string) => Promise<void>;
  loading: boolean;
}

const EXAMPLE_SUGGESTIONS = [
  "Birthday party indoors with yellow decorations and cake",
  "Beach sunset during summer vacation with friends",
  "Outdoor picnic in a park with dogs and sandwiches",
  "Wedding dinner reception in formal dark attire",
];

export default function MemoryInputView({ onSubmitQuery, loading }: MemoryInputViewProps) {
  const [query, setQuery] = useState('');

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      await onSubmitQuery(query.trim());
    }
  };

  return (
    <div className="card-container">
      <h2 className="section-title">What photo are you trying to find?</h2>
      <p className="subtitle">
        Tell me anything you remember — people, setting, clothing, objects, occasion, or even a vague detail.
      </p>

      <form onSubmit={handleSubmit}>
        <textarea
          className="input-textarea"
          placeholder="e.g. That birthday picture from years ago where there were decorations and cake..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          disabled={loading}
          id="memory-query-textarea"
        />

        <div style={{ marginBottom: '1.5rem' }}>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
            Example memory descriptions (click to try):
          </p>
          <div className="example-chips">
            {EXAMPLE_SUGGESTIONS.map((suggestion, idx) => (
              <button
                key={idx}
                type="button"
                className="chip-example"
                onClick={() => setQuery(suggestion)}
              >
                "{suggestion}"
              </button>
            ))}
          </div>
        </div>

        <button
          type="submit"
          className="btn-primary"
          disabled={loading || !query.trim()}
          id="submit-memory-btn"
        >
          {loading ? <span className="spinner" /> : 'Search Memory →'}
        </button>
      </form>
    </div>
  );
}
