// extract.js
// Pulls raw facts out of the pasted award-letter text WITHOUT interpreting
// them: every dollar amount (with the label it sits next to), every date
// (and whether it looks like a deadline), and the academic year.
//
// Every match keeps its original character index in the source text so the UI
// can later highlight it in place, and every "raw" field is the text exactly
// as it appeared, so amounts and dates can be shown to the family verbatim and
// never rephrased. This module is pure: same text in, same object out.

// Amounts: "$5,500", "$500", "$1,234.56", or bare grouped numbers like
// "5,500" / "12,000.00". We require either a "$" or a thousands separator to
// avoid grabbing stray numbers like years or ZIP codes.
const AMOUNT_RE = /\$\s?\d[\d,]*(?:\.\d{1,2})?|\d{1,3}(?:,\d{3})+(?:\.\d{1,2})?/g;

// Dates: "May 1, 2025" / "Sept 1, 2025" and numeric "5/1/2025", "05/01/25",
// and ISO "2025-05-01".
const MONTHS =
  'January|February|March|April|May|June|July|August|September|October|November|December' +
  '|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec';
const DATE_RE = new RegExp(
  `\\b(?:${MONTHS})\\.?\\s+\\d{1,2}(?:st|nd|rd|th)?,?\\s+\\d{4}` + // month-name
    `|\\b\\d{1,2}\\/\\d{1,2}\\/\\d{2,4}\\b` + // m/d/y
    `|\\b\\d{4}-\\d{2}-\\d{2}\\b`, // ISO
  'gi'
);

// Academic year: "2024-2025", "2024–2025", "2024-25", "2024/25".
const ACADEMIC_YEAR_RE = /\b(20\d{2})\s*[-–—/]\s*(20\d{2}|\d{2})\b/;

// Words that make a nearby date look like something the family must act on.
const DEADLINE_RE = /\b(by|due|respond|accept|decline|within|deadline|no later than|return|submit|sign)\b/i;

const MONTH_INDEX = {
  jan: 1, january: 1, feb: 2, february: 2, mar: 3, march: 3, apr: 4, april: 4,
  may: 5, jun: 6, june: 6, jul: 7, july: 7, aug: 8, august: 8, sep: 9, sept: 9,
  september: 9, oct: 10, october: 10, nov: 11, november: 11, dec: 12, december: 12,
};

// Find the start and end index of the line that contains `index`.
function lineBounds(text, index) {
  let start = text.lastIndexOf('\n', index - 1) + 1; // 0 if not found
  let end = text.indexOf('\n', index);
  if (end === -1) end = text.length;
  return { start, end };
}

// Zero-pad to two digits.
function pad(n) {
  return String(n).padStart(2, '0');
}

// Turn a raw date string into an ISO "YYYY-MM-DD", or null if we can't be sure.
function toIso(raw) {
  const cleaned = raw.trim().replace(/\.$/, '');

  // Month-name form: "May 1, 2025"
  const nameMatch = cleaned.match(/^([A-Za-z]+)\.?\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})$/);
  if (nameMatch) {
    const month = MONTH_INDEX[nameMatch[1].toLowerCase()];
    if (!month) return null;
    return `${nameMatch[3]}-${pad(month)}-${pad(Number(nameMatch[2]))}`;
  }

  // Numeric form: "5/1/2025" or "05/01/25"
  const numMatch = cleaned.match(/^(\d{1,2})\/(\d{1,2})\/(\d{2,4})$/);
  if (numMatch) {
    let year = Number(numMatch[3]);
    if (year < 100) year += 2000;
    return `${year}-${pad(Number(numMatch[1]))}-${pad(Number(numMatch[2]))}`;
  }

  // ISO form: "2025-05-01"
  if (/^\d{4}-\d{2}-\d{2}$/.test(cleaned)) return cleaned;

  return null;
}

// Parse a raw amount string ("$5,500.00") into a number (5500).
function toNumber(raw) {
  return Number(raw.replace(/[^0-9.]/g, ''));
}

function extractAmounts(text) {
  const amounts = [];
  for (const m of text.matchAll(AMOUNT_RE)) {
    const raw = m[0];
    const index = m.index;
    const endIndex = index + raw.length;
    const { start, end } = lineBounds(text, index);

    // The label is the text on the same line before the amount. If the amount
    // comes first on the line, fall back to the text after it.
    let before = text.slice(start, index);
    let label = before.replace(/[\s:.–—-]+$/, '').trim();
    let labelStartInLine = before.length - before.trimStart().length;
    let labelIndex = start + labelStartInLine;

    if (!label) {
      const after = text.slice(endIndex, end);
      label = after.replace(/^[\s:.–—-]+/, '').trim();
      labelIndex = label ? endIndex + (after.length - after.trimStart().length) : index;
    }

    amounts.push({
      value: toNumber(raw),
      raw,
      index,
      endIndex,
      label,
      labelIndex,
      line: text.slice(start, end).trim(),
    });
  }
  return amounts;
}

function extractDates(text) {
  const dates = [];
  for (const m of text.matchAll(DATE_RE)) {
    const raw = m[0];
    const index = m.index;
    const { start, end } = lineBounds(text, index);
    const context = text.slice(start, end).trim();

    // A date is a deadline if a deadline word sits on the same line, or just
    // before it in the preceding stretch of text.
    const lookBehind = text.slice(Math.max(0, index - 40), index);
    const isDeadline = DEADLINE_RE.test(context) || DEADLINE_RE.test(lookBehind);

    dates.push({
      raw,
      iso: toIso(raw),
      index,
      endIndex: index + raw.length,
      isDeadline,
      context,
    });
  }
  return dates;
}

function extractAcademicYear(text) {
  const m = text.match(ACADEMIC_YEAR_RE);
  if (!m) return null;
  return { raw: m[0], index: m.index };
}

/**
 * Extract raw amounts, dates, and academic year from award-letter text.
 * @param {string} text
 * @returns {{ academicYear: object|null, amounts: object[], dates: object[] }}
 */
export function extract(text) {
  const source = typeof text === 'string' ? text : '';
  return {
    academicYear: extractAcademicYear(source),
    amounts: extractAmounts(source),
    dates: extractDates(source),
  };
}
