// Tests for the deterministic honest-cost calculator.

import { describe, it, expect } from 'vitest';
import { honestCost, estimateRepayment } from './honestCost.js';
import { FEDERAL_LOAN_RATE } from './constants.js';

// A classified letter: COA 32,000; grants 13,500; loans 5,500; work-study 2,500.
const ITEMS = [
  { label: 'Estimated Cost of Attendance', value: 32000, category: 'COST' },
  { label: 'Federal Pell Grant', value: 5500, category: 'GRANT' },
  { label: 'Institutional Scholarship', value: 8000, category: 'GRANT' },
  { label: 'Direct Subsidized Loan', value: 3500, category: 'LOAN' },
  { label: 'Direct Unsubsidized Loan', value: 2000, category: 'LOAN' },
  { label: 'Federal Work-Study', value: 2500, category: 'WORK_STUDY' },
  { label: 'Widget Assistance Fund', value: 1000, category: 'UNKNOWN' },
];

describe('honestCost()', () => {
  const result = honestCost(ITEMS);

  it('uses the explicit cost-of-attendance line', () => {
    expect(result.costOfAttendance).toBe(32000);
  });

  it('adds grants and scholarships into gift aid', () => {
    expect(result.gift).toBe(13500);
  });

  it('computes what the family actually pays (COA − gift)', () => {
    expect(result.familyPays).toBe(18500);
  });

  it('splits the remainder into loans, work-study, and cash needed', () => {
    expect(result.loans).toBe(5500);
    expect(result.workStudy).toBe(2500);
    expect(result.cashNeeded).toBe(10500); // 18500 − 5500 − 2500
  });

  it('ignores UNKNOWN items in the totals', () => {
    // 1,000 Widget fund is neither gift nor loan nor work-study.
    expect(result.gift + result.loans + result.workStudy).toBe(21500);
  });

  it('sums cost components when there is no explicit total line', () => {
    const components = [
      { label: 'Tuition', value: 20000, category: 'COST' },
      { label: 'Room and Board', value: 10000, category: 'COST' },
      { label: 'Books and Supplies', value: 1500, category: 'COST' },
      { label: 'Pell Grant', value: 5000, category: 'GRANT' },
    ];
    const r = honestCost(components);
    expect(r.costOfAttendance).toBe(31500);
    expect(r.familyPays).toBe(26500);
  });
});

describe('estimateRepayment()', () => {
  it('uses the federal rate constant by default', () => {
    const r = estimateRepayment(5500);
    expect(r.rate).toBe(FEDERAL_LOAN_RATE);
    expect(r.years).toBe(10);
  });

  it('computes a plausible 10-year payoff on $5,500 at 6.39%', () => {
    const r = estimateRepayment(5500);
    // ~$62/mo, ~$7,460 total, ~$1,960 interest.
    expect(r.monthlyPayment).toBeCloseTo(62.15, 1);
    expect(r.totalPaid).toBeGreaterThan(7400);
    expect(r.totalPaid).toBeLessThan(7500);
    expect(r.totalInterest).toBeCloseTo(r.totalPaid - r.principal, 5);
  });

  it('returns zeros when there are no loans', () => {
    const r = estimateRepayment(0);
    expect(r.monthlyPayment).toBe(0);
    expect(r.totalPaid).toBe(0);
    expect(r.totalInterest).toBe(0);
  });

  it('handles a zero interest rate without dividing by zero', () => {
    const r = estimateRepayment(1200, 0, 10);
    expect(r.monthlyPayment).toBe(10); // 1200 / 120
    expect(r.totalPaid).toBe(1200);
    expect(r.totalInterest).toBe(0);
  });
});
