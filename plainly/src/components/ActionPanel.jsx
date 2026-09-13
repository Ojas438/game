// ActionPanel.jsx
// "What you must do and by when." Lists the deadlines found in the letter as
// rows — the date and its surrounding sentence shown VERBATIM from the source
// text, never rephrased. It sits full width at the top of the results grid in
// the largest type on the page. The heading always shows; when there are no
// deadlines it says "None found" rather than hiding.

export default function ActionPanel({ dates }) {
  const deadlines = dates.filter((d) => d.isDeadline);

  return (
    <section className="card action-panel span-all">
      <h2>What you must do and by when</h2>

      {deadlines.length === 0 ? (
        <p className="none-found">None found</p>
      ) : (
        <ul className="deadlines">
          {deadlines.map((d, i) => (
            <li key={i}>
              {/* Date and sentence are verbatim from the letter. */}
              <span className="deadline-date">{d.raw}</span>
              <span className="deadline-context">&ldquo;{d.context}&rdquo;</span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
