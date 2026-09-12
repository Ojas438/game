// UnknownList.jsx
// Lists every line item the classifier could not identify, so the family can
// check whether it is free money or something they have to pay back. Plainly
// never guesses on these — it asks the human. The amounts are shown verbatim.

export default function UnknownList({ lineItems }) {
  const unknowns = lineItems.filter((i) => i.category === 'UNKNOWN');

  if (unknowns.length === 0) {
    return (
      <section className="card unknown-list ok">
        <h2>Nothing unclear</h2>
        <p>Every line item was recognized. Still, double-check against your letter.</p>
      </section>
    );
  }

  return (
    <section className="card unknown-list">
      <h2>Please review these {unknowns.length} item{unknowns.length > 1 ? 's' : ''}</h2>
      <p className="hint">
        Plainly couldn't tell if these are free money or money you must repay. Check your
        letter and decide.
      </p>
      <ul>
        {unknowns.map((item, i) => (
          <li key={i}>
            <span className="unknown-label">{item.label || '(no label found)'}</span>
            <span className="unknown-amount">{item.raw}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
