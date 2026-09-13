// UnknownList.jsx
// Lists every line item the classifier couldn't identify, so the family can
// decide what each one is. Plainly never guesses these — the user chooses a
// category from the dropdown (which re-runs the deterministic math), and can
// optionally ask the AI helper to *suggest* categories. The suggestion only
// pre-fills the dropdown; the human still confirms, and the numbers are never
// computed by the AI.

import { useState } from 'react';
import { suggestCategories } from '../ai/assist.js';

const CHOICES = [
  { value: 'UNKNOWN', label: 'Not sure yet' },
  { value: 'GRANT', label: 'Grant / scholarship (free money)' },
  { value: 'LOAN', label: 'Loan (must repay)' },
  { value: 'WORK_STUDY', label: 'Work-study (must earn)' },
  { value: 'COST', label: 'A cost of attending' },
];

export default function UnknownList({ lineItems, onReclassify }) {
  const [suggestions, setSuggestions] = useState({}); // label -> reason
  const [status, setStatus] = useState(null); // 'loading' | 'error' | null
  const [message, setMessage] = useState('');

  // Items still marked UNKNOWN, paired with their position in the full list so
  // reclassifying updates the right one.
  const unknowns = lineItems
    .map((item, index) => ({ item, index }))
    .filter(({ item }) => item.category === 'UNKNOWN');

  async function askAi() {
    setStatus('loading');
    setMessage('');
    try {
      const { suggestions: result } = await suggestCategories(
        unknowns.map(({ item }) => ({ label: item.label, raw: item.raw }))
      );
      const byLabel = {};
      result.forEach((s, i) => {
        const { index } = unknowns[i];
        byLabel[unknowns[i].item.label] = s.reason;
        if (s.category && s.category !== 'UNKNOWN') onReclassify(index, s.category);
      });
      setSuggestions(byLabel);
      setStatus(null);
    } catch (err) {
      setStatus('error');
      setMessage(err.message);
    }
  }

  if (unknowns.length === 0) {
    return (
      <section className="card unknown-list ok">
        <h2>Nothing left to review</h2>
        <p>Every line item is now categorized. Double-check against your letter.</p>
      </section>
    );
  }

  return (
    <section className="card unknown-list">
      <div className="unknown-header">
        <h2>
          Please review {unknowns.length} item{unknowns.length > 1 ? 's' : ''}
        </h2>
        <button className="link-button" onClick={askAi} disabled={status === 'loading'}>
          {status === 'loading' ? 'Asking…' : 'Suggest with AI'}
        </button>
      </div>
      <p className="hint">
        Plainly couldn&rsquo;t tell if these are free money or money you must repay. Pick a
        category and the totals update instantly.
      </p>
      {status === 'error' && <p className="ingest-error">{message}</p>}

      <ul>
        {unknowns.map(({ item, index }) => (
          <li key={index}>
            <div className="unknown-row">
              <span className="unknown-label">{item.label || '(no label found)'}</span>
              <span className="unknown-amount">{item.raw}</span>
              <select
                className="category-select"
                value={item.category}
                onChange={(e) => onReclassify(index, e.target.value)}
              >
                {CHOICES.map((c) => (
                  <option key={c.value} value={c.value}>
                    {c.label}
                  </option>
                ))}
              </select>
            </div>
            {suggestions[item.label] && (
              <p className="ai-reason">AI: {suggestions[item.label]}</p>
            )}
          </li>
        ))}
      </ul>
    </section>
  );
}
