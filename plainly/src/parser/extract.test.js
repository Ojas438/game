// Tests for the extractor and classifier. These use realistic award-letter
// text so the parser is exercised the way a real paste would exercise it.

import { describe, it, expect } from 'vitest';
import { extract } from './extract.js';
import { classify } from './classify.js';

const SAMPLE = `Financial Aid Award Notification
Academic Year 2024-2025

Estimated Cost of Attendance: $32,000

Federal Pell Grant            $5,500
Institutional Scholarship     $8,000
Direct Subsidized Loan        $3,500
Direct Unsubsidized Loan      $2,000
Federal Work-Study            $2,500
Widget Assistance Fund        $1,000

You must accept or decline this award by May 1, 2025.
Return the signed form no later than 06/15/2025.`;

describe('extract() — amounts', () => {
  const { amounts } = extract(SAMPLE);

  it('finds every dollar amount', () => {
    const values = amounts.map((a) => a.value);
    expect(values).toEqual([32000, 5500, 8000, 3500, 2000, 2500, 1000]);
  });

  it('keeps the raw text of each amount verbatim', () => {
    expect(amounts[0].raw).toBe('$32,000');
    expect(amounts[1].raw).toBe('$5,500');
  });

  it('attaches the label next to each amount', () => {
    expect(amounts[0].label).toBe('Estimated Cost of Attendance');
    expect(amounts[1].label).toBe('Federal Pell Grant');
    expect(amounts[3].label).toBe('Direct Subsidized Loan');
  });

  it('records a source index that points back at the amount', () => {
    const a = amounts[1];
    expect(SAMPLE.slice(a.index, a.endIndex)).toBe(a.raw);
  });

  it('handles a bare grouped number without a dollar sign', () => {
    const { amounts: bare } = extract('Tuition   12,500');
    expect(bare).toHaveLength(1);
    expect(bare[0].value).toBe(12500);
    expect(bare[0].label).toBe('Tuition');
  });

  it('does not grab a plain year as an amount', () => {
    const { amounts: none } = extract('For the 2025 school year.');
    expect(none).toHaveLength(0);
  });
});

describe('extract() — dates', () => {
  const { dates } = extract(SAMPLE);

  it('finds the dates and normalizes them to ISO', () => {
    const may = dates.find((d) => d.raw === 'May 1, 2025');
    expect(may).toBeDefined();
    expect(may.iso).toBe('2025-05-01');

    const jun = dates.find((d) => d.raw === '06/15/2025');
    expect(jun.iso).toBe('2025-06-15');
  });

  it('flags dates near deadline words as deadlines', () => {
    const may = dates.find((d) => d.raw === 'May 1, 2025');
    expect(may.isDeadline).toBe(true); // "accept or decline ... by"

    const jun = dates.find((d) => d.raw === '06/15/2025');
    expect(jun.isDeadline).toBe(true); // "no later than"
  });

  it('keeps the surrounding line verbatim for display', () => {
    const may = dates.find((d) => d.raw === 'May 1, 2025');
    expect(may.context).toBe('You must accept or decline this award by May 1, 2025.');
  });

  it('does not flag a plain date with no deadline wording', () => {
    const { dates: d } = extract('Awarded on March 3, 2025 for enrollment.');
    expect(d[0].isDeadline).toBe(false);
  });
});

describe('extract() — academic year', () => {
  it('finds the academic year', () => {
    const { academicYear } = extract(SAMPLE);
    expect(academicYear.raw).toBe('2024-2025');
  });

  it('returns null when there is none', () => {
    expect(extract('No year here.').academicYear).toBeNull();
  });
});

describe('classify()', () => {
  it('sorts federal programs into the right category', () => {
    expect(classify('Federal Pell Grant').category).toBe('GRANT');
    expect(classify('Institutional Scholarship').category).toBe('GRANT');
    expect(classify('Direct Subsidized Loan').category).toBe('LOAN');
    expect(classify('Direct Unsubsidized Loan').category).toBe('LOAN');
    expect(classify('Parent PLUS Loan').category).toBe('LOAN');
    expect(classify('Federal Work-Study').category).toBe('WORK_STUDY');
    expect(classify('Estimated Cost of Attendance').category).toBe('COST');
    expect(classify('Tuition and Fees').category).toBe('COST');
  });

  it('falls through to UNKNOWN and never guesses', () => {
    expect(classify('Widget Assistance Fund').category).toBe('UNKNOWN');
    expect(classify('').category).toBe('UNKNOWN');
    expect(classify(null).category).toBe('UNKNOWN');
  });
});
