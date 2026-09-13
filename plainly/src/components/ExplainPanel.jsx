// ExplainPanel.jsx
// The "simplified" side of the Plain English version card. A button asks the AI
// helper to describe, in plain language, the numbers the deterministic
// calculator ALREADY computed — it is told to use only those figures and never
// to compute anything. Renders as an inner pane (no card of its own); the
// wrapping PlainEnglish card supplies the heading.

import { useState } from 'react';
import { explainBreakdown } from '../ai/assist.js';

export default function ExplainPanel({ cost, academicYear }) {
  const [status, setStatus] = useState('idle'); // idle | loading | done | error
  const [text, setText] = useState('');
  const [error, setError] = useState('');

  async function handleExplain() {
    setStatus('loading');
    setError('');
    try {
      const { explanation } = await explainBreakdown(cost, academicYear);
      setText(explanation);
      setStatus('done');
    } catch (err) {
      setError(err.message);
      setStatus('error');
    }
  }

  return (
    <div className="pe-side">
      <div className="pe-side-head">
        <h3>Simplified</h3>
        <button className="secondary-button" onClick={handleExplain} disabled={status === 'loading'}>
          {status === 'loading' ? 'Writing…' : status === 'done' ? 'Rewrite' : 'Explain with AI'}
        </button>
      </div>
      {status === 'idle' && (
        <p className="none-found">Tap &ldquo;Explain with AI&rdquo; for a plain-language summary.</p>
      )}
      {status === 'error' && <p className="ingest-error">{error}</p>}
      {status === 'done' &&
        text
          .split(/\n{2,}/)
          .filter(Boolean)
          .map((para, i) => (
            <p key={i} className="explain-text">
              {para}
            </p>
          ))}
    </div>
  );
}
