import { Braces, Database, Scale } from "lucide-react";
import { ControlChart } from "../components/ControlChart";
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
        <SectionLabel index="METHOD / 01">Frozen before OOS</SectionLabel>
        <div className="intro-grid">
          <h1>
            A control that failed.
            <em>A desk that learned.</em>
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
        <SectionLabel index="02 / 04">Locked policy</SectionLabel>
        <div className="policy-list">
          {policy.map((item) => (
            <article key={item.label}>
              <p>{item.label}</p>
              <strong>{item.value}</strong>
              <span>{item.note}</span>
            </article>
          ))}
        </div>
      </section>

      <section className="method-section">
        <SectionLabel index="03 / 04">Negative-control result</SectionLabel>
        <div className="control-layout method-control">
          <ControlChart />
          <div className="method-metrics">
            <div><span>IS</span><strong>79 days</strong><small>7 traded · 10 trades</small></div>
            <div><span>IS Sharpe</span><strong>-1.58</strong><small>15 bps / side</small></div>
            <div><span>IS Sharpe</span><strong>-2.96</strong><small>25 bps / side</small></div>
            <div><span>OOS provisional</span><strong>-5.57</strong><small>23 days · 5 trades · 15 bps</small></div>
            <div><span>Weekend</span><strong>0 / 26</strong><small>entries / nights</small></div>
          </div>
        </div>
      </section>

      <section className="method-section">
        <SectionLabel index="04 / 04">Separation of duties</SectionLabel>
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
