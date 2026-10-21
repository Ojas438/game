// Runs the exported XGBoost model in the browser.
// For each tree: start at the top, answer its yes/no question, and keep going until
// reaching a leaf. Each leaf is a small "vote" for one of the 11 answers. Add up all the
// votes, then turn the totals into percentages that add up to 100% (the "softmax" step).
function predictNextScore(model, inputs) {
  const totals = model.base.slice();
  for (const tree of model.trees) {
    let node = 0;
    while (tree.l[node] !== -1) {
      node = inputs[tree.f[node]] < tree.v[node] ? tree.l[node] : tree.r[node];
    }
    totals[tree.c] += tree.v[node];
  }
  const biggest = Math.max(...totals);
  const exps = totals.map((t) => Math.exp(t - biggest));
  const sum = exps.reduce((a, b) => a + b, 0);
  return exps.map((e) => e / sum);
}

if (typeof module !== "undefined") module.exports = { predictNextScore };
