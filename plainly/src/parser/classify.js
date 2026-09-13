// classify.js
// Sorts a single line-item label into exactly one category:
// GRANT, LOAN, WORK_STUDY, COST, or UNKNOWN.
//
// Why it exists: an award letter lumps loans and grants together under the
// word "award." Knowing which is which is the whole point of Plainly, so this
// is deliberately its own small, testable step. All the knowledge lives in
// the data table (programs.js); this file is only the matching loop. If a
// label matches nothing, it returns UNKNOWN — we never guess.

import { PROGRAM_TABLE, CATEGORIES } from './programs.js';

/**
 * @param {string} label - the text next to a dollar amount, e.g. "Direct Subsidized Loan"
 * @returns {{ category: string, matched: RegExp | null }}
 */
// Explanatory / marketing text — borrowing limits, financing options, payment
// plans — often sits right next to a dollar figure ("Parents may borrow up to
// $20,000"). That figure is NOT awarded aid, so we refuse to categorize it and
// let it fall through to UNKNOWN for the user to review, rather than silently
// counting a borrowing limit as free money or an awarded loan.
const INFO_RE = /\bborrow|financing option|aggregate limit|payment plan|loan simulator|repayment calculator|may qualify|up to \$/i;

export function classify(label) {
  if (!label || typeof label !== 'string') {
    return { category: CATEGORIES.UNKNOWN, matched: null };
  }

  if (INFO_RE.test(label)) {
    return { category: CATEGORIES.UNKNOWN, matched: null };
  }

  for (const entry of PROGRAM_TABLE) {
    for (const pattern of entry.patterns) {
      // Patterns here are intentionally non-global, so .test() is stateless.
      if (pattern.test(label)) {
        return { category: entry.category, matched: pattern };
      }
    }
  }

  return { category: CATEGORIES.UNKNOWN, matched: null };
}
