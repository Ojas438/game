// SourceView.jsx
// The "original" side of the Plain English version card. Shows the letter's own
// text, verbatim, with every amount and date highlighted in place and colored
// by category. Lets a family check our reading against their actual letter.
// Renders as an inner pane (no card of its own); the wrapping PlainEnglish card
// supplies the heading.

import { buildRanges, buildSegments } from '../parser/highlight.js';

export default function SourceView({ text, analysis }) {
  const segments = buildSegments(text, buildRanges(analysis));

  return (
    <div className="pe-side">
      <div className="pe-side-head">
        <h3>Original letter</h3>
      </div>
      <p className="pe-legend">
        Grants green · loans red · work-study amber · costs gray · unrecognized outlined ·
        deadline dates underlined.
      </p>
      <pre className="source-text">
        {segments.map((seg, i) => {
          if (seg.kind === null) return <span key={i}>{seg.text}</span>;
          const cls =
            seg.kind === 'amount'
              ? `mark mark-${(seg.category || 'unknown').toLowerCase()}`
              : `mark mark-date${seg.isDeadline ? ' mark-deadline' : ''}`;
          return (
            <span key={i} className={cls}>
              {seg.text}
            </span>
          );
        })}
      </pre>
    </div>
  );
}
