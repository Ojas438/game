// SourceView.jsx
// Shows the original pasted letter with every amount and date highlighted in
// place, colored by what Plainly decided each one is. This lets the family
// check our reading against their actual letter, line by line.

import { buildRanges, buildSegments } from '../parser/highlight.js';

export default function SourceView({ text, analysis }) {
  const segments = buildSegments(text, buildRanges(analysis));

  return (
    <section className="card source-view">
      <h2>Your letter, marked up</h2>
      <p className="hint">
        Grants are green, loans red, work-study amber, costs gray, and unrecognized
        amounts are outlined. Dates that look like deadlines are underlined.
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
    </section>
  );
}
