// analyze.js
// The one function the UI calls. It ties the pipeline together:
//   1. extract() pulls raw amounts, dates, and the academic year from the text
//   2. classify() labels each amount as GRANT / LOAN / WORK_STUDY / COST / UNKNOWN
//   3. honestCost() turns the classified items into the real numbers
// It adds no interpretation of its own — it just wires the pure pieces
// together and returns one object for the results view.

import { extract } from './extract.js';
import { classify } from './classify.js';
import { honestCost } from '../calc/honestCost.js';

/**
 * @param {string} text - raw pasted award-letter text
 * @returns {{ academicYear, dates, lineItems, cost }}
 */
export function analyze(text) {
  const { academicYear, amounts, dates } = extract(text);

  const lineItems = amounts.map((amount) => {
    const { category, matched } = classify(amount.label);
    return {
      ...amount,
      category,
      // Keep the matched pattern as a readable string for debugging/highlighting.
      matched: matched ? matched.source : null,
    };
  });

  const cost = honestCost(lineItems);

  return { academicYear, dates, lineItems, cost };
}
