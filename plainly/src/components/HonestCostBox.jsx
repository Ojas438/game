// HonestCostBox.jsx
// The heart of the results: shows the honest arithmetic the letter hides —
// cost of attendance minus free money equals what the family really pays —
// then breaks that number into loans, work-study, and cash, and shows the
// long-term cost of the loans after ~10 years of repayment.

import { formatMoney, formatPercent } from '../format.js';

export default function HonestCostBox({ cost }) {
  const { costOfAttendance, gift, familyPays, loans, workStudy, cashNeeded, repayment } = cost;

  return (
    <section className="card cost-box">
      <h2>What you'll actually pay</h2>

      <div className="math">
        <Row label="Cost of attendance" value={costOfAttendance} />
        <Row label="Free money (grants & scholarships)" value={-gift} muted />
        <div className="rule" />
        <Row label="What your family actually pays" value={familyPays} emphasis />
      </div>

      <h3 className="breakdown-title">How that gets covered</h3>
      <div className="breakdown">
        <Chip title="Loans (must repay)" value={loans} tone="loan" />
        <Chip title="Work-study (must earn)" value={workStudy} tone="work" />
        <Chip title="Cash you need to find" value={cashNeeded} tone="cash" />
      </div>

      {loans > 0 && (
        <p className="repayment-note">
          Those <strong>{formatMoney(repayment.principal)}</strong> in loans, repaid over{' '}
          {repayment.years} years at {formatPercent(repayment.rate)}, cost about{' '}
          <strong>{formatMoney(repayment.monthlyPayment, true)}/month</strong> —{' '}
          <strong>{formatMoney(repayment.totalPaid)}</strong> in total, which is{' '}
          <strong>{formatMoney(repayment.totalInterest)}</strong> more than you borrowed.
        </p>
      )}
    </section>
  );
}

function Row({ label, value, muted, emphasis }) {
  return (
    <div className={`math-row${emphasis ? ' emphasis' : ''}${muted ? ' muted' : ''}`}>
      <span>{label}</span>
      <span className="num">{formatMoney(value)}</span>
    </div>
  );
}

function Chip({ title, value, tone }) {
  return (
    <div className={`chip chip-${tone}`}>
      <div className="chip-value">{formatMoney(value)}</div>
      <div className="chip-title">{title}</div>
    </div>
  );
}
