// Tests for the source-highlighting helpers.

import { describe, it, expect } from 'vitest';
import { buildRanges, buildSegments } from './highlight.js';

describe('buildSegments()', () => {
  it('reconstructs the original text exactly from its segments', () => {
    const text = 'Pell Grant $5,500 due May 1, 2025';
    const ranges = [
      { start: 11, end: 17, kind: 'amount', category: 'GRANT' },
      { start: 22, end: 33, kind: 'date', isDeadline: true },
    ];
    const segs = buildSegments(text, ranges);
    expect(segs.map((s) => s.text).join('')).toBe(text);
  });

  it('marks matched stretches and leaves plain text with kind null', () => {
    const text = 'Loan $3,500';
    const segs = buildSegments(text, [{ start: 5, end: 11, kind: 'amount', category: 'LOAN' }]);
    expect(segs[0]).toEqual({ text: 'Loan ', kind: null });
    expect(segs[1].kind).toBe('amount');
    expect(segs[1].category).toBe('LOAN');
  });

  it('drops a range that overlaps one already emitted', () => {
    const text = 'abcdefgh';
    const ranges = [
      { start: 0, end: 4, kind: 'amount' },
      { start: 2, end: 6, kind: 'date' }, // overlaps the first
    ];
    const segs = buildSegments(text, ranges);
    expect(segs.map((s) => s.text).join('')).toBe(text);
    expect(segs.filter((s) => s.kind === 'date')).toHaveLength(0);
  });
});

describe('buildRanges()', () => {
  it('turns line items and dates into ranges', () => {
    const ranges = buildRanges({
      lineItems: [{ index: 0, endIndex: 5, category: 'GRANT' }],
      dates: [{ index: 10, endIndex: 20, isDeadline: true }],
    });
    expect(ranges).toEqual([
      { start: 0, end: 5, kind: 'amount', category: 'GRANT' },
      { start: 10, end: 20, kind: 'date', isDeadline: true },
    ]);
  });
});
