// highlight.js
// Turns the source text plus the extracted matches into a flat list of
// display segments, so the UI can show the ORIGINAL letter with amounts and
// dates colored in place. This is where the source indices captured during
// extraction finally pay off. Pure and testable — no React here.

/**
 * Build the highlight ranges from an analysis result.
 * @param {{ lineItems: object[], dates: object[] }} analysis
 * @returns {Array<{start:number, end:number, kind:string, category?:string, isDeadline?:boolean}>}
 */
export function buildRanges({ lineItems = [], dates = [] } = {}) {
  const ranges = [];
  for (const item of lineItems) {
    ranges.push({ start: item.index, end: item.endIndex, kind: 'amount', category: item.category });
  }
  for (const date of dates) {
    ranges.push({ start: date.index, end: date.endIndex, kind: 'date', isDeadline: date.isDeadline });
  }
  return ranges;
}

/**
 * Split text into non-overlapping segments. Plain stretches have kind === null;
 * matched stretches carry their range info. If two ranges overlap, the one that
 * starts first wins and the other is dropped (amounts and dates don't normally
 * overlap, but we never want to emit garbled text).
 * @param {string} text
 * @param {Array<{start:number,end:number}>} ranges
 * @returns {Array<{text:string, kind:string|null, category?:string, isDeadline?:boolean}>}
 */
export function buildSegments(text, ranges) {
  const sorted = ranges
    .filter((r) => r.end > r.start)
    .sort((a, b) => a.start - b.start);

  const segments = [];
  let cursor = 0;

  for (const r of sorted) {
    if (r.start < cursor) continue; // overlaps a range we already emitted
    if (r.start > cursor) {
      segments.push({ text: text.slice(cursor, r.start), kind: null });
    }
    segments.push({
      text: text.slice(r.start, r.end),
      kind: r.kind,
      category: r.category,
      isDeadline: r.isDeadline,
    });
    cursor = r.end;
  }

  if (cursor < text.length) {
    segments.push({ text: text.slice(cursor), kind: null });
  }

  return segments;
}
