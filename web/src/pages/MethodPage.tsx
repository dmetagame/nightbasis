import { Braces, Database, Scale } from "lucide-react";
import { SectionLabel } from "../components/SectionLabel";
import { freezeHash } from "../data/research";

const policy = [
  { label: "Weeknight price control", value: "z ≥ 1.0", note: "rQQQ primary · rSPY fallback" },
  { label: "Weekend price control", value: "z ≥ 1.5", note: "BTC + ETH only · no washout" },
  { label: "Desk washout label", value: "z ≥ 1.25", note: "No qualifying event · y < 0 · weeknight" },
  { label: "Event response band", value: "|y| < 1.0%", note: "Incomplete requires material information" },
  { label: "Signed information", value: "≥ 0.65", note: "direction × materiality × confidence" },
];

export function MethodPage() {
  return (
    <div className="page-wrap method-page">
      <section className="page-intro">
        <SectionLabel index="Method">Frozen before the OOS read</SectionLabel>
        <div className="intro-grid">
          <h1>
            Freeze the rule.
            <em>Then believe the result.</em>
          </h1>
          <div className="intro-copy">
            <p>
              Price-only alpha was closed, not cosmetically improved. Its fixed
              model remains the baseline against which the Desk explains evidence.
            </p>
          </div>
        </div>
      </section>

      <section className="method-section">
        <div className="freeze-card">
          <div>
            <p className="eyebrow">Immutable reference</p>
            <h2>Freeze 0898cca</h2>
          </div>
          <code>{freezeHash}</code>
          <div className="freeze-meta">
            <span>Commit</span><strong>c92b9bd</strong>
            <span>Retuned</span><strong>No</strong>
            <span>Factors traded</span><strong>Never</strong>
          </div>
        </div>
      </section>

      <section className="method-section">
        <SectionLabel index="Policy">Five definitions, held constant</SectionLabel>
        <dl className="policy-list">
          {policy.map((item) => (
            <div key={item.label}>
              <dt>{item.label}</dt>
              <dd><strong>{item.value}</strong><span>{item.note}</span></dd>
            </div>
          ))}
        </dl>
      </section>

      <section className="method-section">
        <SectionLabel index="Result">The negative control stayed negative</SectionLabel>
        <div className="method-metrics metric-tiles">
          <article><span>IS window</span><strong>79 days</strong><small>7 traded · 10 trades</small></article>
          <article><span>IS Sharpe · 15 bps</span><strong>−1.58</strong><small>per side</small></article>
          <article><span>IS Sharpe · 25 bps</span><strong>−2.96</strong><small>per side</small></article>
          <article><span>OOS provisional</span><strong>−5.57</strong><small>23 days · 5 trades</small></article>
        </div>
      </section>

      <section className="method-section">
        <SectionLabel index="Duties">Each layer has one job</SectionLabel>
        <div className="proof-grid architecture-grid">
          <article>
            <Database aria-hidden="true" />
            <p className="eyebrow">Inputs</p>
            <h3>Frozen evidence</h3>
            <p>rToken and factor observations plus company sources available at each snapshot.</p>
          </article>
          <article>
            <Braces aria-hidden="true" />
            <p className="eyebrow">LLM contract</p>
            <h3>Explain only</h3>
            <p>Human-v1 fixture caches mirror temperature-zero structured output.</p>
          </article>
          <article>
            <Scale aria-hidden="true" />
            <p className="eyebrow">Deterministic desk</p>
            <h3>Label or reject</h3>
            <p>Python owns quality gates, timing, reasons, and the final no-trade memo.</p>
          </article>
        </div>
      </section>
    </div>
  );
}
