// App.jsx
// Top-level component. It owns the pasted text and the analysis result, wires
// the input to the parser, and lets the user (optionally with AI suggestions)
// re-label UNKNOWN items — which re-runs the DETERMINISTIC calculator. All the
// real work happens in the pure modules under src/parser and src/calc; the AI
// helper never touches the numbers.

import { useState } from 'react';
import { analyze } from './parser/analyze.js';
import { honestCost } from './calc/honestCost.js';
import AwardInput from './components/AwardInput.jsx';
import HonestCostBox from './components/HonestCostBox.jsx';
import UnknownList from './components/UnknownList.jsx';
import ActionPanel from './components/ActionPanel.jsx';
import SourceView from './components/SourceView.jsx';
import ExplainPanel from './components/ExplainPanel.jsx';

export default function App() {
  const [text, setText] = useState('');
  const [result, setResult] = useState(null);
  // The exact text that was analyzed, so highlighting lines up even if the
  // user keeps editing the textarea afterward.
  const [analyzedText, setAnalyzedText] = useState('');

  function handleBreakItDown() {
    setResult(analyze(text));
    setAnalyzedText(text);
  }

  // Re-label one line item and recompute the honest cost. The recompute is the
  // same deterministic function used everywhere — reclassifying never asks an
  // AI for a number.
  function reclassify(itemIndex, category) {
    setResult((prev) => {
      const lineItems = prev.lineItems.map((item, i) =>
        i === itemIndex ? { ...item, category, userSet: true } : item
      );
      return { ...prev, lineItems, cost: honestCost(lineItems) };
    });
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
            <ExplainPanel cost={result.cost} academicYear={result.academicYear?.raw} />
            <ActionPanel dates={result.dates} />
            <UnknownList lineItems={result.lineItems} onReclassify={reclassify} />
            <SourceView text={analyzedText} analysis={result} />
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>
          The math runs entirely on your device. The optional AI helper (the
          &ldquo;Explain&rdquo; and &ldquo;Suggest&rdquo; buttons) sends only the line-item
          names and computed totals to our server when you click it — never your whole
          letter, and only if you ask. Numbers are estimates; confirm important figures
          with your school.
        </p>
      </footer>
    </div>
  );
}
