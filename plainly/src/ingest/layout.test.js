// Tests for the column-aware PDF line grouper.

import { describe, it, expect } from 'vitest';
import { groupIntoLines } from './layout.js';

// Helper: a text fragment at (x, y) with a width.
const f = (str, x, y, w) => ({ str, x, y, w });

describe('groupIntoLines()', () => {
  it('reads a single-column page top-to-bottom, left-to-right', () => {
    const items = [
      f('Pell Grant', 40, 200, 80),
      f('$5,500', 300, 200, 40),
      f('Direct Loan', 40, 180, 90),
      f('$3,500', 300, 180, 40),
    ];
    expect(groupIntoLines(items, 612)).toEqual(['Pell Grant $5,500', 'Direct Loan $3,500']);
  });

  it('keeps side-by-side columns apart instead of merging them', () => {
    // Left column: an aid row. Right column: unrelated marketing text at the
    // same vertical position, separated by a wide empty gutter.
    const items = [
      f('Pell Grant $5,500', 40, 200, 150),
      f('Parents may borrow up to $20,000', 380, 200, 190),
      f('Direct Loan $3,500', 40, 180, 150),
      f('Consider federal loans first', 380, 180, 190),
    ];
    const lines = groupIntoLines(items, 612);
    // The $20,000 blurb must NOT be stapled onto the Pell Grant row.
    expect(lines).toContain('Pell Grant $5,500');
    expect(lines.some((l) => /Pell Grant.*20,000/.test(l))).toBe(false);
    expect(lines.some((l) => /borrow up to \$20,000/.test(l))).toBe(true);
  });
});
