// AwardInput.jsx
// The paste box: a large textarea for the raw award-letter text and the
// "Break it down" button. It holds no logic of its own — it hands the text up
// to App, which runs the parser.

export default function AwardInput({ text, onChange, onSubmit }) {
  return (
    <section className="card input-card">
      <label htmlFor="award-text" className="input-label">
        Paste the text of your financial aid award letter
      </label>
      <textarea
        id="award-text"
        className="award-textarea"
        value={text}
        onChange={(e) => onChange(e.target.value)}
        placeholder={
          'Estimated Cost of Attendance: $32,000\n' +
          'Federal Pell Grant            $5,500\n' +
          'Direct Subsidized Loan        $3,500\n' +
          'Federal Work-Study            $2,500\n\n' +
          'Accept or decline by May 1, 2025.'
        }
        rows={14}
        spellCheck={false}
      />
      <button className="primary-button" onClick={onSubmit} disabled={!text.trim()}>
        Break it down
      </button>
    </section>
  );
}
