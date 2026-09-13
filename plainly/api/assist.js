// api/assist.js
// Vercel serverless function — the ONLY place Plainly talks to an AI, and it
// runs on the server so the API key never reaches the browser. There are still
// no user accounts and no database.
//
// Two jobs, both advisory and both kept away from the arithmetic:
//   action: "suggest" → propose a category for line items the deterministic
//                        classifier marked UNKNOWN. The user confirms; only
//                        then does the (still deterministic) calculator re-run.
//   action: "explain" → put the numbers WE already computed into plain English.
//                        The model is given the finished figures and told not to
//                        invent or recompute any of them.
//
// The honest-cost math lives in src/calc and never runs here.

import Anthropic from '@anthropic-ai/sdk';

// Default to the most capable model. This is a small, infrequent call, but if
// cost matters you can switch to a cheaper model (e.g. "claude-haiku-4-5")
// here — it's the only line you need to change.
const MODEL = 'claude-opus-5';

const CATEGORIES = ['GRANT', 'LOAN', 'WORK_STUDY', 'COST', 'UNKNOWN'];

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }
  if (!process.env.ANTHROPIC_API_KEY) {
    return res.status(503).json({ error: 'AI features are not configured on this deployment.' });
  }

  const body = typeof req.body === 'string' ? safeParse(req.body) : req.body || {};
  const client = new Anthropic();

  try {
    if (body.action === 'suggest') {
      return res.status(200).json(await suggest(client, body.items || []));
    }
    if (body.action === 'explain') {
      return res.status(200).json(await explain(client, body.summary || {}, body.academicYear));
    }
    return res.status(400).json({ error: 'Unknown action.' });
  } catch (err) {
    console.error('assist error:', err);
    return res.status(502).json({ error: 'The AI request failed. Please try again.' });
  }
}

// Suggest a category for each UNKNOWN item. The model only labels; it never
// touches money. We validate every category against our fixed list so a stray
// value can't leak into the app.
async function suggest(client, items) {
  const list = items
    .map((it, i) => `${i + 1}. "${it.label}" (amount as written: ${it.raw})`)
    .join('\n');

  const response = await client.messages.create({
    model: MODEL,
    max_tokens: 1024,
    output_config: { effort: 'low' },
    system:
      'You help a family read a college financial aid award letter. For each ' +
      'line item, decide which category best fits its NAME:\n' +
      '- GRANT: free money that is never repaid (grants, scholarships, waivers)\n' +
      '- LOAN: money that must be repaid, usually with interest\n' +
      '- WORK_STUDY: money earned by working a job\n' +
      '- COST: part of what college costs (tuition, fees, room, board, books)\n' +
      '- UNKNOWN: genuinely unclear — use this rather than guessing\n\n' +
      'Reply with ONLY a JSON array, one object per item, in order:\n' +
      '[{"category": "...", "reason": "short plain-language reason"}]\n' +
      'Use exactly these category names. If you are not confident, use UNKNOWN.',
    messages: [{ role: 'user', content: `Classify these line items:\n${list}` }],
  });

  const text = response.content.find((b) => b.type === 'text')?.text ?? '';
  const parsed = extractJsonArray(text);

  const suggestions = items.map((it, i) => {
    const s = parsed[i] || {};
    const category = CATEGORIES.includes(s.category) ? s.category : 'UNKNOWN';
    return { label: it.label, category, reason: typeof s.reason === 'string' ? s.reason : '' };
  });

  return { suggestions };
}

// Explain the already-computed numbers in plain language. The figures are
// passed in and the model is told to use them verbatim and not compute anything.
async function explain(client, summary, academicYear) {
  const s = summary || {};
  const facts =
    `Academic year: ${academicYear || 'not stated'}\n` +
    `Cost of attendance: $${num(s.costOfAttendance)}\n` +
    `Free money (grants & scholarships): $${num(s.gift)}\n` +
    `What the family actually pays: $${num(s.familyPays)}\n` +
    `Loans (must repay): $${num(s.loans)}\n` +
    `Work-study (must earn): $${num(s.workStudy)}\n` +
    `Cash the family must find: $${num(s.cashNeeded)}\n` +
    `Estimated total loan repayment over ${s.repayment?.years ?? 10} years: ` +
    `$${num(s.repayment?.totalPaid)} (of which $${num(s.repayment?.totalInterest)} is interest)`;

  const response = await client.messages.create({
    model: MODEL,
    max_tokens: 1024,
    output_config: { effort: 'low' },
    system:
      'You explain a college financial aid award to a family in plain, warm, ' +
      'non-judgmental language at about an 8th-grade reading level. ' +
      'CRITICAL RULES:\n' +
      '- Use ONLY the numbers provided. Do not calculate, estimate, or invent ' +
      'any figure. If a number is not given, do not mention it.\n' +
      '- Do not give financial advice or tell them what to choose.\n' +
      '- Emphasize the difference between money they keep (grants) and money ' +
      'they must pay back (loans).\n' +
      'Write 2–3 short paragraphs. No headings, no bullet lists.',
    messages: [{ role: 'user', content: `Explain this breakdown:\n${facts}` }],
  });

  const explanation = response.content.find((b) => b.type === 'text')?.text ?? '';
  return { explanation };
}

function num(v) {
  return Math.round(Number(v) || 0).toLocaleString('en-US');
}

function safeParse(s) {
  try {
    return JSON.parse(s);
  } catch {
    return {};
  }
}

// Pull the first JSON array out of the model's text, defensively.
function extractJsonArray(text) {
  const start = text.indexOf('[');
  const end = text.lastIndexOf(']');
  if (start === -1 || end === -1 || end < start) return [];
  try {
    const arr = JSON.parse(text.slice(start, end + 1));
    return Array.isArray(arr) ? arr : [];
  } catch {
    return [];
  }
}
