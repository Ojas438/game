// programs.js
// DATA ONLY — no logic here. This is the lookup table that the classifier
// (classify.js) reads to sort each line item from an award letter into one
// category. Colleges use many different names for the same program, so the
// goal is to make adding a new name a one-line edit here instead of touching
// code.
//
// Each entry pairs a category with a list of case-insensitive patterns. The
// first pattern that matches a label wins. Order the entries most-specific
// first where names could overlap. Anything that matches nothing falls
// through to UNKNOWN in classify.js — we never guess.

export const CATEGORIES = {
  GRANT: 'GRANT', // free money — never repaid
  LOAN: 'LOAN', // must be repaid, usually with interest
  WORK_STUDY: 'WORK_STUDY', // money you must earn by working
  COST: 'COST', // part of what college costs
  UNKNOWN: 'UNKNOWN', // could not be identified — flag for the user
};

export const PROGRAM_TABLE = [
  {
    category: CATEGORIES.LOAN,
    patterns: [
      /direct\s+subsidized/i,
      /direct\s+unsubsidized/i,
      /subsidized\s+loan/i,
      /unsubsidized\s+loan/i,
      /parent\s*plus/i,
      /grad(uate)?\s*plus/i,
      /\bplus\s+loan/i,
      /perkins/i,
      /stafford/i,
      /\bloan\b/i,
    ],
  },
  {
    category: CATEGORIES.WORK_STUDY,
    patterns: [
      /federal\s+work[\s-]*study/i,
      /work[\s-]*study/i,
      /\bfws\b/i,
    ],
  },
  {
    category: CATEGORIES.GRANT,
    patterns: [
      /pell\s*grant/i,
      /\bseog\b/i,
      /supplemental\s+educational\s+opportunity\s+grant/i,
      /teach\s+grant/i,
      /iraq.*afghanistan.*service\s+grant/i,
      /\bgrant\b/i,
      /scholarship/i,
      /\bwaiver\b/i,
    ],
  },
  {
    category: CATEGORIES.COST,
    patterns: [
      /cost\s+of\s+attendance/i,
      /estimated\s+cost/i,
      /total\s+(cost|budget|charges)/i,
      /\btuition\b/i,
      /\bfees?\b/i,
      /room\s*(and|&)?\s*board/i,
      /\bhousing\b/i,
      /meal\s*plan/i,
      /books?\s*(and|&)?\s*supplies/i,
      /\bbooks\b/i,
      /transportation/i,
      /personal\s+expenses/i,
    ],
  },
];
