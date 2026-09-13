// format.js
// Small display helpers. Formatting only — these never change a number's value,
// they just present it. The calculator produces the numbers; this rounds them
// for the screen.

export function formatMoney(amount, showCents = false) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: showCents ? 2 : 0,
    maximumFractionDigits: showCents ? 2 : 0,
  }).format(amount || 0);
}

export function formatPercent(rate) {
  return `${(rate * 100).toFixed(2)}%`;
}
