// ExplainPanel.jsx
// An optional "explain this in plain language" button. It sends the numbers
// Plainly ALREADY computed to the AI helper and shows the plain-English
// explanation it writes back. The AI is told to use only the figures we give
// it and never to compute anything — the trustworthy numbers stay in the
// deterministic calculator; this just narrates them.

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
    <section className="card explain-panel">
      <div className="explain-header">
        <h2>Explain this in plain language</h2>
        <button
          className="secondary-button"
          onClick={handleExplain}
          disabled={status === 'loading'}
        >
          {status === 'loading' ? 'Writing…' : status === 'done' ? 'Rewrite' : 'Explain'}
        </button>
      </div>
      <p className="hint">Optional. Uses AI to describe the numbers above — it does not change them.</p>
      {status === 'error' && <p className="ingest-error">{error}</p>}
      {status === 'done' &&
        text
          .split(/\n{2,}/)
          .filter(Boolean)
          .map((para, i) => <p key={i} className="explain-text">{para}</p>)}
    </section>
  );
}
