# Plainly

Families get college aid award letters that mix loans in with grants under the
word "award," subtract the loans from the cost, and show a bottom line that
looks like what you pay. It isn't. **Plainly** takes the pasted text of an award
letter and shows what a family will actually pay out of pocket — separating
money you keep from money you must repay.

Built for the Congressional App Challenge. React + Vite, plain JavaScript,
runs entirely in the browser. No backend, no accounts, no data leaves the page.

## This milestone

Paste award-letter text → get an honest breakdown. **No OCR, camera, or AI/LLM
anywhere.** All parsing and math are deterministic JavaScript.

## Run it

```bash
npm install
npm run dev      # start the app
npm test         # run parser + calculator unit tests
npm run build    # production build (deploys to Vercel)
```

## How it works

The logic is pure functions, kept separate from the React components so it can
be read and tested on its own.

```
src/
  parser/
    extract.js     pulls every $ amount (with its label), every date
                   (and whether it's a deadline), and the academic year —
                   keeping each match's source index for later highlighting
    classify.js    sorts one line item into GRANT / LOAN / WORK_STUDY / COST
                   / UNKNOWN — never guesses
    programs.js    DATA-ONLY lookup table driving the classifier (federal
                   programs + common variants); add a name in one line
    analyze.js     runs extract → classify → honestCost and returns one object
  calc/
    constants.js   FEDERAL_LOAN_RATE and repayment term — update yearly
    honestCost.js  deterministic math: COA − grants = what you pay, split into
                   loans / work-study / cash, plus the ~10-year repayment total
  components/       React views (input box, honest-cost box, deadlines, unknowns)
```

### The honest number

```
cost of attendance
− grants and scholarships (free money)
= what your family actually pays        → then split into loans / work-study / cash
```

Loans also get a ~10-year repayment estimate at the current federal rate (a
named constant in `src/calc/constants.js`).

### Two rules the code keeps

- **Never guess.** Anything the classifier can't identify becomes `UNKNOWN` and
  is flagged for the user to review, rather than silently counted as aid.
- **Show deadlines and amounts verbatim.** The "what you must do" panel repeats
  the letter's own sentences and dates — never a paraphrase.
