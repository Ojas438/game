// TermsExplained.jsx
// "Terms explained" card. A small glossary of the kinds of aid found in this
// letter — term on the left, a one-sentence plain-English definition on the
// right. Terms are shown only when that kind of item appears in the letter, so
// families see definitions for what they actually got. The heading always
// shows; with nothing recognized it says "None found".
//
// Presentation only. Definitions are fixed copy; nothing is computed here.

// Order matters — most important first.
const GLOSSARY = [
  ['GRANT', 'Grant / scholarship', 'Free money for college that you never have to pay back.'],
  ['LOAN', 'Loan', 'Borrowed money you must pay back later, usually with added interest.'],
  ['WORK_STUDY', 'Work-study', 'A part-time job — you earn this money by working; it is not paid to you upfront.'],
  ['COST', 'Cost of attendance', "The school's total estimated yearly cost, including expenses it never bills you for."],
];

export default function TermsExplained({ lineItems }) {
  const present = new Set(lineItems.map((i) => i.category));
  const terms = GLOSSARY.filter(([cat]) => present.has(cat));

  return (
    <section className="card terms span-all">
      <h2>Terms explained</h2>
      {terms.length === 0 ? (
        <p className="none-found">None found</p>
      ) : (
        <div className="terms-list">
          {terms.map(([cat, term, def]) => (
            <div className="term-row" key={cat}>
              <span className="term-name">{term}</span>
              <span className="term-def">{def}</span>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
