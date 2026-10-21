// Checks that the web demo's math gives the same answers as Python's XGBoost.
// Run with:   node check_demo.js
const fs = require("fs");
const { predictNextScore } = require("./demo/predict.js");

const model = JSON.parse(fs.readFileSync("demo/model.json"));
const cases = JSON.parse(fs.readFileSync("results/check_cases.json"));
let worst = 0;
cases.inputs.forEach((x, i) => {
  const p = predictNextScore(model, x);
  p.forEach((v, k) => { worst = Math.max(worst, Math.abs(v - cases.python_probs[i][k])); });
});
console.log(`Checked ${cases.inputs.length} plays. Biggest difference from Python: ${(worst * 100).toFixed(4)} percentage points`);
process.exit(worst < 0.0005 ? 0 : 1);
