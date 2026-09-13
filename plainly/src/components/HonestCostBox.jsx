// HonestCostBox.jsx
// "Your real cost" card. Shows the honest arithmetic the letter hides as one
// row per number — cost of attendance, minus free money, equals what the family
// actually pays (bold total) — then the rows that make up that number and the
// long-term loan cost. No sentences: every figure gets its own row.
//
// This component is presentation only. The numbers come straight from the
// deterministic calculator in src/calc; nothing is computed here.

import { formatMoney, formatPercent } from '../format.js';

export default function HonestCostBox({ cost }) {
  const { costOfAttendance, gift, familyPays, loans, workStudy, cashNeeded, repayment } = cost;

  return (
    <section className="card cost-box">
      <h2>Your real cost</h2>

      <div className="rows">
        <Row label="Cost of attendance" value={costOfAttendance} />
        <Row label="Free money (grants & scholarships)" value={-gift} good />
        <div className="rule" />
        <Row label="What your family actually pays" value={familyPays} total />
      </div>

      <h3 className="rows-subhead">How that gets covered</h3>
      <div className="rows">
        <Row label="Loans (must repay)" value={loans} tone="loan" />
        <Row label="Work-study (must earn)" value={workStudy} tone="work" />
        <Row label="Cash you need to find" value={cashNeeded} tone="cash" />
      </div>

      {loans > 0 && (
        <>
          <h3 className="rows-subhead">
            Loan cost over {repayment.years} years @ {formatPercent(repayment.rate)}
          </h3>
          <div className="rows">
            <Row label="Monthly payment" value={repayment.monthlyPayment} cents />
            <Row label="Total repaid" value={repayment.totalPaid} />
            <Row label="Interest on top of what you borrowed" value={repayment.totalInterest} tone="loan" />
          </div>
        </>
      )}
    </section>
  );
}

function Row({ label, value, total, good, tone, cents }) {
  const cls =
    'row' + (total ? ' row-total' : '') + (good ? ' row-good' : '') + (tone ? ` row-${tone}` : '');
  return (
    <div className={cls}>
      <span className="row-label">{label}</span>
      <span className="row-num">{formatMoney(value, cents)}</span>
    </div>
  );
}
