// layout.js
// Turns the loose, positioned text fragments a PDF gives us into readable lines
// — WITHOUT letting side-by-side page columns bleed into each other.
//
// Award letters are often laid out in two or three columns (the aid table on
// the left, marketing text on the right). A naive "group everything on the same
// line" approach merges those columns, so a Parent PLUS blurb on the right gets
// stapled onto a grant row on the left and the numbers come out nonsense. This
// module first finds the vertical whitespace "gutters" that run down the whole
// page, splits the fragments into column regions at those gutters, and only
// then reads each column top-to-bottom. Pure and testable — no PDF/DOM here.

/**
 * @param {Array<{str:string, x:number, y:number, w:number}>} items
 *   x = left edge, y = vertical position (higher = nearer top), w = width.
 * @param {number} [pageWidth] optional page width; inferred from items if absent.
 * @returns {string[]} lines, column by column, each column top-to-bottom.
 */
export function groupIntoLines(items, pageWidth) {
  const frags = items.filter((it) => it.str && it.str.trim());
  if (frags.length === 0) return [];

  const maxX = Math.max(pageWidth || 0, ...frags.map((f) => f.x + f.w));
  if (maxX <= 0) return rowsToLines(frags);

  // Mark which horizontal slices of the page contain any text.
  const BINS = 120;
  const covered = new Array(BINS).fill(false);
  for (const f of frags) {
    const b0 = Math.max(0, Math.floor((f.x / maxX) * BINS));
    const b1 = Math.min(BINS - 1, Math.floor(((f.x + f.w) / maxX) * BINS));
    for (let b = b0; b <= b1; b++) covered[b] = true;
  }

  // A gutter is a run of empty slices wide enough to separate columns. Ignore
  // the page's outer margins — only interior gutters split columns.
  const minGutter = Math.max(3, Math.round(BINS * 0.045));
  const candidates = [];
  let run = 0;
  for (let b = 0; b <= BINS; b++) {
    const empty = b < BINS && !covered[b];
    if (empty) {
      run++;
    } else {
      if (run >= minGutter) {
        const centerBin = b - run / 2;
        const x = (centerBin / BINS) * maxX;
        if (x > maxX * 0.1 && x < maxX * 0.9) candidates.push(x);
      }
      run = 0;
    }
  }

  // Only split at a gutter that has a real second column of PROSE to its right
  // (wide text fragments across multiple rows). This is what separates a true
  // two-column layout from the ordinary gap between a label and its dollar
  // amount — an amount column is narrow, so it never triggers a split.
  const wide = frags.filter((f) => f.w > maxX * 0.18);
  const cuts = candidates.filter(
    (cx) => new Set(wide.filter((f) => f.x >= cx).map((f) => Math.round(f.y))).size >= 2
  );

  if (cuts.length === 0) return rowsToLines(frags); // single column

  // Build column x-ranges from the cuts and assign each fragment by its center.
  const bounds = [0, ...cuts, Infinity];
  const columns = bounds.slice(0, -1).map((lo, i) => ({ lo, hi: bounds[i + 1], frags: [] }));
  for (const f of frags) {
    const cx = f.x + f.w / 2;
    (columns.find((c) => cx >= c.lo && cx < c.hi) || columns[columns.length - 1]).frags.push(f);
  }

  const lines = [];
  for (const col of columns) lines.push(...rowsToLines(col.frags));
  return lines;
}

// Group fragments into rows by vertical position, read left-to-right.
function rowsToLines(frags) {
  const rows = new Map();
  for (const f of frags) {
    const y = Math.round(f.y);
    if (!rows.has(y)) rows.set(y, []);
    rows.get(y).push(f);
  }
  return [...rows.entries()]
    .sort((a, b) => b[0] - a[0]) // top of page first
    .map(([, row]) =>
      row
        .sort((a, b) => a.x - b.x)
        .map((f) => f.str)
        .join(' ')
        .replace(/\s+/g, ' ')
        .trim()
    )
    .filter(Boolean);
}
