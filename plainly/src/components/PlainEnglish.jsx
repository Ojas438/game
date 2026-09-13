// PlainEnglish.jsx
// "Plain English version" card. Full width, spanning the results grid. Places
// the simplified summary and the original marked-up letter side by side so a
// family can compare them; the two panes stack on narrow screens. This is a
// layout wrapper only — the panes do the work.

import ExplainPanel from './ExplainPanel.jsx';
import SourceView from './SourceView.jsx';

export default function PlainEnglish({ cost, academicYear, text, analysis }) {
  return (
    <section className="card plain-english span-all">
      <h2>Plain English version</h2>
      <div className="pe-grid">
        <ExplainPanel cost={cost} academicYear={academicYear} />
        <SourceView text={text} analysis={analysis} />
      </div>
    </section>
  );
}
