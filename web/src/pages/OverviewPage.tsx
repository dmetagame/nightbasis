import { useRef } from "react";
import { Link } from "react-router-dom";
import { ArrowRight } from "lucide-react";
import { gsap } from "gsap";
import { useGSAP } from "@gsap/react";
import { ReplayPanel } from "../components/ReplayPanel";
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
        <p className="hero-kicker hero-reveal">The overnight information desk for rTokens</p>
        <h1 className="hero-title hero-reveal">
          Overnight rTokens do not need another bot that always buys.
        </h1>
        <p className="hero-copy hero-reveal">
          NightBasis compares the tape with point-in-time company evidence—and
          makes standing down a first-class product decision.
        </p>
        <div className="hero-actions hero-reveal">
          <Link className="primary-link" to="/desk">
            Replay the desk <ArrowRight size={16} aria-hidden="true" />
          </Link>
          <Link className="secondary-link" to="/method">Method</Link>
        </div>
      </section>

      <section className="overview-section home-replay">
        <SectionLabel index="Live desk">A frozen night, replayed point by point</SectionLabel>
        <ReplayPanel compact />
      </section>

      <section className="overview-section">
        <SectionLabel index="Three nights">No hindsight. No manufactured conviction.</SectionLabel>
        <div className="fixture-ledger">
          {deskFixtures.map((fixture) => {
            const close = fixture.snapshots[3];
            return (
              <article className="ledger-row" key={fixture.id}>
                <div>
                  <p>{fixture.eyebrow}</p>
                  <h2>{fixture.symbol} <span>{fixture.date}</span></h2>
                </div>
                <p className="ledger-evidence">{fixture.evidence}</p>
                <div className="ledger-read">
                  <span className={close.yPercent < 0 ? "is-negative" : ""}>
                    {close.yPercent > 0 ? "+" : ""}{close.yPercent.toFixed(2)}%
                  </span>
                  <small>No trade</small>
                </div>
              </article>
            );
          })}
        </div>
      </section>

      <section className="overview-section control-section">
        <SectionLabel index="Negative control">The failed alpha became the product decision</SectionLabel>
        <div className="metric-tiles">
          <article><span>IS Sharpe · 15 bps</span><strong>−1.58</strong><small>79 days</small></article>
          <article><span>Trades</span><strong>10</strong><small>7 traded days</small></article>
          <article><span>Provisional OOS</span><strong>−5.57</strong><small>15 bps per side</small></article>
          <article><span>Weekend entries</span><strong>0 / 26</strong><small>nights observed</small></article>
        </div>
        <div className="control-note">
          <p>Price alone lost money. We published the result and did not retune.</p>
          <code>{freezeHash}</code>
        </div>
      </section>
    </div>
  );
}
