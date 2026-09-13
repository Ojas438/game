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

## Deploying to Vercel

The app lives in the `plainly/` subdirectory, so in the Vercel project settings
set **Root Directory** to `plainly`. Framework (Vite), build command, output
directory, and the SPA rewrite are already declared in `plainly/vercel.json`.

To turn on the **optional** AI helper (see below), add an `ANTHROPIC_API_KEY`
environment variable in the Vercel project. Without it, the app still works
fully — the AI buttons just report that the feature isn't configured.

## Input options

Paste text, click **Try a sample**, or **upload a PDF/image** or **take a
photo** of the letter. PDFs with a real text layer are read directly; scanned
PDFs and photos are run through OCR (Tesseract.js). All of this happens in the
browser — the file never leaves the device — and the extracted text lands in the
textarea so you can fix any OCR mistakes before parsing.

## The optional AI layer

Everything that matters — parsing and the honest-cost math — is deterministic
JavaScript and needs no AI. Two **optional, advisory** AI features sit on top,
behind a Vercel serverless function (`api/assist.js`) so the API key stays on
the server and never ships to the browser. There are still no accounts and no
database.

- **Suggest** a category for items the classifier marked UNKNOWN. The
  suggestion only pre-fills a dropdown; you confirm, and the deterministic
  calculator re-runs.
- **Explain** the breakdown in plain language. The model is given the numbers
  Plainly already computed and told to use them verbatim — it never calculates
  anything.

**The AI never touches the numbers.** It labels and it narrates; the math lives
entirely in `src/calc`.

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
    highlight.js   pure helpers to color amounts/dates in the original text
  ingest/
    readFile.js    browser-only OCR / PDF text extraction (nothing leaves device)
  ai/
    assist.js      thin client for the optional AI helper (advisory only)
  components/       React views (input, honest-cost, deadlines, unknowns,
                   marked-up source, plain-language explanation)
api/
  assist.js        Vercel serverless AI proxy — keeps the API key server-side;
                   only labels UNKNOWN items and narrates, never does math
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
