// App.jsx
// Top-level component. It owns two pieces of state — the pasted text and the
// analysis result — and wires the input to the parser and the parser's output
// to the results view. All the real work happens in the pure modules under
// src/parser and src/calc; this file just moves data between them and the UI.

import { useState } from 'react';
import { analyze } from './parser/analyze.js';
import AwardInput from './components/AwardInput.jsx';
import HonestCostBox from './components/HonestCostBox.jsx';
import UnknownList from './components/UnknownList.jsx';
import ActionPanel from './components/ActionPanel.jsx';

export default function App() {
  const [text, setText] = useState('');
  const [result, setResult] = useState(null);

  function handleBreakItDown() {
    setResult(analyze(text));
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Plainly</h1>
        <p className="tagline">
          Award letters mix loans in with grants and call it all &ldquo;aid.&rdquo; Paste
          yours to see what you actually pay.
        </p>
      </header>

      <main className="layout">
        <AwardInput text={text} onChange={setText} onSubmit={handleBreakItDown} />

        {result && (
          <div className="results">
            {result.academicYear && (
              <p className="academic-year">Academic year: {result.academicYear.raw}</p>
            )}
            <HonestCostBox cost={result.cost} />
            <ActionPanel dates={result.dates} />
            <UnknownList lineItems={result.lineItems} />
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>
          Plainly does the math on your device. Nothing you paste leaves your browser.
          Numbers are estimates — confirm important figures with your school.
        </p>
      </footer>
    </div>
  );
}
