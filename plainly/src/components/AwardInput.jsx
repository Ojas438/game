// AwardInput.jsx
// The paste box: a large textarea for the raw award-letter text and the
// "Break it down" button, plus "Try a sample" and file/photo upload. Uploading
// runs OCR/PDF text-extraction in the browser (see ingest/readFile.js) and
// drops the resulting text into the textarea, where the user can fix any OCR
// mistakes before parsing. This component owns only the upload UI state; the
// parsing still happens up in App.

import { useRef, useState } from 'react';
import { SAMPLE_LETTER } from '../sampleLetter.js';
import { readFile } from '../ingest/readFile.js';

export default function AwardInput({ text, onChange, onSubmit }) {
  const fileRef = useRef(null);
  const cameraRef = useRef(null);
  const [status, setStatus] = useState(null); // { stage, progress } while reading
  const [error, setError] = useState(null);

  async function handleFile(e) {
    const file = e.target.files?.[0];
    e.target.value = ''; // allow re-selecting the same file
    if (!file) return;

    setError(null);
    setStatus({ stage: 'Starting', progress: 0 });
    try {
      const { text: extracted } = await readFile(file, setStatus);
      if (extracted.trim()) {
        onChange(extracted);
      } else {
        setError("Couldn't find any text in that file. Try pasting the text instead.");
      }
    } catch (err) {
      setError('Something went wrong reading that file. Try pasting the text instead.');
      console.error(err);
    } finally {
      setStatus(null);
    }
  }

  const busy = status !== null;

  return (
    <section className="card input-card">
      <div className="input-header">
        <label htmlFor="award-text" className="input-label">
          Paste the text of your financial aid award letter
        </label>
        <div className="input-actions">
          <button className="link-button" onClick={() => onChange(SAMPLE_LETTER)} disabled={busy}>
            Try a sample
          </button>
          <button className="link-button" onClick={() => fileRef.current?.click()} disabled={busy}>
            Upload PDF or image
          </button>
          <button className="link-button" onClick={() => cameraRef.current?.click()} disabled={busy}>
            Take a photo
          </button>
        </div>
      </div>

      <input
        ref={fileRef}
        type="file"
        accept="application/pdf,image/*,.txt"
        hidden
        onChange={handleFile}
      />
      <input
        ref={cameraRef}
        type="file"
        accept="image/*"
        capture="environment"
        hidden
        onChange={handleFile}
      />

      {busy && (
        <p className="ingest-status">
          {status.stage}
          {status.progress > 0 ? ` — ${Math.round(status.progress * 100)}%` : '…'}
        </p>
      )}
      {error && <p className="ingest-error">{error}</p>}

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
      {(text.trim() && !busy) && (
        <p className="hint ocr-hint">
          If this came from a photo or PDF, glance over it for scanning mistakes before
          breaking it down.
        </p>
      )}
      <button className="primary-button" onClick={onSubmit} disabled={!text.trim() || busy}>
        Break it down
      </button>
    </section>
  );
}
