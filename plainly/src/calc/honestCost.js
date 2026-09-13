// honestCost.js
// The honest-cost math. Deterministic JavaScript only — no AI, no guessing,
// no network. Given the classified line items from a letter it computes:
//
//   cost of attendance
//   − grants and scholarships (free money)
//   = what the family actually pays
//
// and splits that remainder into loans, work-study, and cash needed. It also
// estimates the ~10-year repayment total on the loans using a standard
// amortization formula and the rate in constants.js.
//
// The same inputs always produce the same numbers, so the results can be
// trusted and unit-tested.

import { FEDERAL_LOAN_RATE, REPAYMENT_YEARS } from './constants.js';
import { CATEGORIES } from '../parser/programs.js';

function sumByCategory(items, category) {
  return items
    .filter((i) => i.category === category)
    .reduce((total, i) => total + i.value, 0);
}

// Prefer an explicit "Cost of Attendance" / total line if the letter has one.
function findTotalCostLine(items) {
  return items.find(
    (i) =>
      i.category === CATEGORIES.COST &&
      /cost\s+of\s+attendance|estimated\s+cost|total\s+(cost|budget|charges)/i.test(i.label)
  );
}

/**
 * Estimate the standard 10-year repayment on a loan principal.
 * Uses the fixed-rate amortization formula. If the rate is 0, payments are
 * just principal spread evenly across the term.
 * @returns {{principal, rate, years, monthlyPayment, totalPaid, totalInterest}}
 */
export function estimateRepayment(
  principal,
  annualRate = FEDERAL_LOAN_RATE,
  years = REPAYMENT_YEARS
) {
  if (principal <= 0) {
    return { principal: 0, rate: annualRate, years, monthlyPayment: 0, totalPaid: 0, totalInterest: 0 };
  }

  const months = years * 12;
  const monthlyRate = annualRate / 12;

  const monthlyPayment =
    monthlyRate === 0
      ? principal / months
      : (principal * monthlyRate) / (1 - Math.pow(1 + monthlyRate, -months));

  const totalPaid = monthlyPayment * months;

  return {
    principal,
    rate: annualRate,
    years,
    monthlyPayment,
    totalPaid,
    totalInterest: totalPaid - principal,
  };
}

/**
 * Compute the honest cost from classified line items.
 * @param {Array<{category:string, value:number, label:string}>} lineItems
 * @returns {object} the honest-cost summary
 */
export function honestCost(lineItems = []) {
  const totalCostLine = findTotalCostLine(lineItems);

  // If there's an explicit total, use it. Otherwise add up the cost pieces.
  // (Never add both, or we'd double-count.)
  const costOfAttendance = totalCostLine
    ? totalCostLine.value
    : lineItems
        .filter((i) => i.category === CATEGORIES.COST)
        .reduce((total, i) => total + i.value, 0);

  const gift = sumByCategory(lineItems, CATEGORIES.GRANT); // grants + scholarships
  const loans = sumByCategory(lineItems, CATEGORIES.LOAN);
  const workStudy = sumByCategory(lineItems, CATEGORIES.WORK_STUDY);

  const familyPays = costOfAttendance - gift; // the honest bottom line
  const cashNeeded = familyPays - loans - workStudy; // gap after borrowing/earning

  return {
    costOfAttendance,
    gift,
    loans,
    workStudy,
    familyPays,
    cashNeeded,
    repayment: estimateRepayment(loans),
  };
}
