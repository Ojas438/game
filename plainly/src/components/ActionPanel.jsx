// ActionPanel.jsx
// "What you must do, and by when." Lists the deadlines found in the letter.
// Everything here is shown VERBATIM from the source text — the date and the
// surrounding sentence are never rephrased, so the family acts on the letter's
// own words, not our paraphrase.

export default function ActionPanel({ dates }) {
  const deadlines = dates.filter((d) => d.isDeadline);

  return (
    <section className="card action-panel">
      <h2>What you must do, and by when</h2>

      {deadlines.length === 0 ? (
        <p className="hint">
          No clear deadlines were found in the text. Check your letter carefully — deadlines
          are easy to bury.
        </p>
      ) : (
        <ul>
          {deadlines.map((d, i) => (
            <li key={i}>
              <span className="deadline-date">{d.raw}</span>
              {/* Verbatim source sentence — never reworded. */}
              <span className="deadline-context">&ldquo;{d.context}&rdquo;</span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
