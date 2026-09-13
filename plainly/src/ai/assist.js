// ai/assist.js
// Thin browser-side client for the /api/assist serverless function. It sends a
// request and returns the result, or throws a friendly Error the UI can show.
// The AI here is optional and advisory — nothing it returns is ever fed into
// the honest-cost math. If the deployment has no API key, these calls fail
// gracefully and the app still works without them.

async function post(payload) {
  let res;
  try {
    res = await fetch('/api/assist', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
  } catch {
    throw new Error('Could not reach the AI helper. Check your connection.');
  }

  if (res.status === 503) {
    throw new Error('AI features are not turned on for this site.');
  }
  if (!res.ok) {
    throw new Error('The AI helper had a problem. Please try again.');
  }
  return res.json();
}

/**
 * Ask the AI to suggest categories for UNKNOWN items.
 * @param {Array<{label:string, raw:string}>} items
 * @returns {Promise<{suggestions: Array<{label, category, reason}>}>}
 */
export function suggestCategories(items) {
  return post({ action: 'suggest', items });
}

/**
 * Ask the AI to explain the (already computed) numbers in plain language.
 * @param {object} summary - the honest-cost result
 * @param {string|undefined} academicYear
 * @returns {Promise<{explanation: string}>}
 */
export function explainBreakdown(summary, academicYear) {
  return post({ action: 'explain', summary, academicYear });
}
