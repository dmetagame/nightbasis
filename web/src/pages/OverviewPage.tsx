import { useRef } from "react";
import { Link } from "react-router-dom";
import { ArrowRight, Braces, FileCheck2, ShieldCheck } from "lucide-react";
import { gsap } from "gsap";
import { useGSAP } from "@gsap/react";
import { ControlChart } from "../components/ControlChart";
import { NoTradeMark } from "../components/NoTradeMark";
import { SectionLabel } from "../components/SectionLabel";
import { deskFixtures, freezeHash } from "../data/research";
import { useReducedMotion } from "../hooks/useReducedMotion";

export function OverviewPage() {
  const root = useRef<HTMLDivElement>(null);
  const reduced = useReducedMotion();

  useGSAP(
    () => {
      if (reduced) {
        gsap.set(".hero-reveal", { opacity: 1, clearProps: "transform" });
        return;
      }
      gsap.from(".hero-reveal", {
        y: 28,
        opacity: 0,
        duration: 0.9,
        stagger: 0.09,
        ease: "power3.out",
      });
    },
    { scope: root, dependencies: [reduced], revertOnUpdate: true },
  );

  return (
    <div ref={root} className="page-wrap overview-page">
      <section className="hero-section">
        <div className="hero-status hero-reveal">
          <span className="status-dot" aria-hidden="true" />
          Frozen research · 3 nights · 12 stand-downs
        </div>
        <div className="hero-layout">
          <div>
            <p className="eyebrow hero-reveal">After-hours information pricing</p>
            <h1 className="hero-title hero-reveal">
              When the filing and tape disagree,
              <em>restraint is the signal.</em>
            </h1>
          </div>
          <div className="hero-side hero-reveal">
            <p>
              NightBasis Desk pairs a frozen factor baseline with point-in-time
              company evidence. It explains the move, exposes the conflict, and
              refuses to manufacture conviction.
            </p>
            <div className="hero-actions">
              <Link className="primary-link" to="/desk">
                Open live replay <ArrowRight size={15} aria-hidden="true" />
              </Link>
              <Link className="text-link" to="/method">Read the frozen method</Link>
            </div>
          </div>
        </div>
        <div className="hero-verdict hero-reveal">
          <NoTradeMark />
        </div>
      </section>

      <section className="overview-section">
        <SectionLabel index="01 / 03">Three nights, no hindsight</SectionLabel>
        <div className="fixture-ledger">
          {deskFixtures.map((fixture, index) => {
            const close = fixture.snapshots[3];
            return (
              <article className="ledger-row" key={fixture.id}>
                <div className="ledger-index">0{index + 1}</div>
                <div>
                  <p className="eyebrow">{fixture.eyebrow}</p>
                  <h2>{fixture.symbol} · {fixture.date}</h2>
                </div>
                <p className="ledger-evidence">{fixture.evidence}</p>
                <div className="ledger-read">
                  <span>{close.yPercent > 0 ? "+" : ""}{close.yPercent.toFixed(2)}%</span>
                  <code>{close.reason}</code>
                </div>
              </article>
            );
          })}
        </div>
      </section>

      <section className="overview-section control-section">
        <SectionLabel index="02 / 03">The failure is a product decision</SectionLabel>
        <div className="control-layout">
          <div className="control-copy">
            <h2>
              We tested price alone.
              <em>It lost money.</em>
            </h2>
            <p>
              The frozen control produced an IS Sharpe of -1.58 at 15 bps per
              side across 10 trades. Provisional OOS fell to -5.57. Twenty-six
              weekend nights produced zero entries.
            </p>
            <p className="control-decision">
              We did not retune. The failed alpha became the reason to ship an
              evidence desk instead.
            </p>
          </div>
          <ControlChart />
        </div>
      </section>

      <section className="overview-section proof-section">
        <SectionLabel index="03 / 03">Designed to be rejected</SectionLabel>
        <div className="proof-grid">
          <article>
            <FileCheck2 aria-hidden="true" />
            <h3>Point-in-time</h3>
            <p>No 08:30 evidence can change a 16:30 read.</p>
          </article>
          <article>
            <Braces aria-hidden="true" />
            <h3>Structured</h3>
            <p>Temperature-zero JSON is cached and schema checked.</p>
          </article>
          <article>
            <ShieldCheck aria-hidden="true" />
            <h3>Non-executing</h3>
            <p>The LLM explains. Deterministic rules decide. Nothing trades.</p>
          </article>
        </div>
        <div className="freeze-line">
          <span>Frozen price-only control</span>
          <code>{freezeHash}</code>
          <strong>Not retuned</strong>
        </div>
      </section>
    </div>
  );
}
