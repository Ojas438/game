// GrantsVsLoans.jsx
// "Grants vs loans" card. Two columns side by side — money you keep (grants &
// scholarships) and money you repay (loans) — each item on its own row with a
// verbatim dollar amount, and each column with its own bold total. Below them,
// any line items the parser couldn't categorize appear as a short "Needs
// review" list where the user can sort each into keep vs repay (which re-runs
// the deterministic calculator); an optional AI button only pre-fills the
// choice. Column headings always show; empty columns say "None found".
//
// Presentation only — the totals come from the deterministic calculator; the
// per-item lists are the already-extracted line items, filtered for display.

import { useState } from 'react';
import { formatMoney } from '../format.js';
import { suggestCategories } from '../ai/assist.js';

const CHOICES = [
  { value: 'UNKNOWN', label: 'Not sure yet' },
  { value: 'GRANT', label: 'Grant / scholarship (keep)' },
  { value: 'LOAN', label: 'Loan (repay)' },
  { value: 'WORK_STUDY', label: 'Work-study (earn)' },
  { value: 'COST', label: 'A cost of attending' },
];

// Subtotal rows ("Total Scholarships & Grants") are excluded from the totals by
// the calculator, so hide them from these per-item lists too, to stay in sync.
const isSubtotal = (i) => /\btotals?\b|\bsubtotal\b/i.test(i.label || '');

export default function GrantsVsLoans({ lineItems, cost, onReclassify }) {
  const [suggestions, setSuggestions] = useState({});
  const [status, setStatus] = useState(null);
  const [error, setError] = useState('');

  const grants = lineItems.filter((i) => i.category === 'GRANT' && !isSubtotal(i));
  const loans = lineItems.filter((i) => i.category === 'LOAN' && !isSubtotal(i));
  const unknowns = lineItems
    .map((item, index) => ({ item, index }))
    .filter(({ item }) => item.category === 'UNKNOWN');

  async function askAi() {
    setStatus('loading');
    setError('');
    try {
      const { suggestions: result } = await suggestCategories(
        unknowns.map(({ item }) => ({ label: item.label, raw: item.raw }))
      );
      const byLabel = {};
      result.forEach((s, i) => {
        byLabel[unknowns[i].item.label] = s.reason;
        if (s.category && s.category !== 'UNKNOWN') onReclassify(unknowns[i].index, s.category);
      });
      setSuggestions(byLabel);
      setStatus(null);
    } catch (err) {
      setStatus('error');
      setError(err.message);
    }
  }

  return (
    <section className="card gvl">
      <h2>Grants vs loans</h2>
      <div className="gvl-cols">
        <Column title="Money you keep" note="never repaid" items={grants} total={cost.gift} tone="grant" />
        <Column title="Money you repay" note="paid back with interest" items={loans} total={cost.loans} tone="loan" />
      </div>

      <div className="gvl-review">
        <div className="gvl-review-head">
          <h3>Needs review</h3>
          {unknowns.length > 0 && (
            <button className="link-button" onClick={askAi} disabled={status === 'loading'}>
              {status === 'loading' ? 'Asking…' : 'Suggest with AI'}
            </button>
          )}
        </div>
        {status === 'error' && <p className="ingest-error">{error}</p>}
        {unknowns.length === 0 ? (
          <p className="none-found">None found</p>
        ) : (
          <ul className="review-list">
            {unknowns.map(({ item, index }) => (
              <li key={index}>
                <div className="review-row">
                  <span className="row-label">{item.label || '(no label found)'}</span>
                  <span className="row-num">{item.raw}</span>
                  <select
                    className="category-select"
                    value={item.category}
                    onChange={(e) => onReclassify(index, e.target.value)}
                  >
                    {CHOICES.map((c) => (
                      <option key={c.value} value={c.value}>
                        {c.label}
                      </option>
                    ))}
                  </select>
                </div>
                {suggestions[item.label] && <p className="ai-reason">AI: {suggestions[item.label]}</p>}
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}

function Column({ title, note, items, total, tone }) {
  return (
    <div className={`gvl-col gvl-${tone}`}>
      <div className="gvl-col-head">
        <span className="gvl-col-title">{title}</span>
        <span className="gvl-col-note">{note}</span>
      </div>
      {items.length === 0 ? (
        <p className="none-found">None found</p>
      ) : (
        <div className="rows">
          {items.map((it, i) => (
            <div className="row" key={i}>
              {/* Amount shown verbatim from the letter. */}
              <span className="row-label">{it.label || '(no label found)'}</span>
              <span className="row-num">{it.raw}</span>
            </div>
          ))}
        </div>
      )}
      <div className="row row-total">
        <span className="row-label">Total</span>
        <span className="row-num">{formatMoney(total)}</span>
      </div>
    </div>
  );
}
