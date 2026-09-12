// constants.js
// Numbers that change from year to year, kept in one place so they are easy to
// find and update. These are the ONLY tunable inputs to the honest-cost math.

// Federal Direct Loan interest rate for undergraduates.
// Set every year by Congress and published at
// https://studentaid.gov/understand-aid/types/loans/interest-rates
// Current value: 2025–26 undergraduate Direct Subsidized/Unsubsidized rate.
// Update this one number when the new rate is announced.
export const FEDERAL_LOAN_RATE = 0.0639; // 6.39%

// Standard Repayment Plan term used for the ~10-year payoff estimate.
export const REPAYMENT_YEARS = 10;
