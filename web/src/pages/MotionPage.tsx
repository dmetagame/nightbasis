import { useRef, useState } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useGSAP } from "@gsap/react";
import { SectionLabel } from "../components/SectionLabel";
import { deskFixtures } from "../data/research";
import { useReducedMotion } from "../hooks/useReducedMotion";

const techniques = [
  ["01", "Document progress", "A one-pixel measure of the reader's position, scrubbed from zero to max."],
  ["02", "Ink fill", "Clip-path reveals the verdict without moving the page beneath the reader."],
  ["03", "Evidence pin", "The filing remains fixed while four point-in-time tape observations advance."],
  ["04", "Night traverse", "Three frozen sessions move horizontally; the order remains the research order."],
  ["05", "Batch reveal", "Technique notes enter as a cohort rather than unrelated decorative motion."],
  ["06", "Motion restraint", "Reduced motion removes Lenis, pins, scrubs, and large-area translation."],
] as const;

export function MotionPage() {
  const root = useRef<HTMLDivElement>(null);
  const progress = useRef<HTMLDivElement>(null);
  const inkSection = useRef<HTMLElement>(null);
  const filingSection = useRef<HTMLElement>(null);
  const horizontalSection = useRef<HTMLElement>(null);
  const horizontalTrack = useRef<HTMLDivElement>(null);
  const [pinnedIndex, setPinnedIndex] = useState(0);
  const reduced = useReducedMotion();
  const news = deskFixtures[1];

  useGSAP(
    () => {
      if (reduced) {
        gsap.set([progress.current, ".ink-fill", ".technique-card"], {
          clearProps: "all",
        });
        return;
      }

      const media = gsap.matchMedia();
      media.add("(min-width: 768px)", () => {
        gsap.fromTo(
          progress.current,
          { scaleX: 0 },
          {
            scaleX: 1,
            ease: "none",
            scrollTrigger: { start: 0, end: "max", scrub: true },
          },
        );

        gsap.fromTo(
          ".ink-fill",
          { clipPath: "inset(100% 0 0 0)" },
          {
            clipPath: "inset(0% 0 0 0)",
            ease: "none",
            scrollTrigger: {
              trigger: inkSection.current,
              start: "top 78%",
              end: "bottom 35%",
              scrub: 0.45,
            },
          },
        );

        ScrollTrigger.create({
          trigger: filingSection.current,
          start: "top 4rem",
          end: "+=1800",
          pin: true,
          scrub: 0.5,
          anticipatePin: 1,
          onUpdate: (self) => {
            setPinnedIndex(Math.min(3, Math.floor(self.progress * 4)));
          },
        });

        const track = horizontalTrack.current;
        const section = horizontalSection.current;
        if (track && section) {
          gsap.to(track, {
            x: () => -(track.scrollWidth - window.innerWidth),
            ease: "none",
            scrollTrigger: {
              trigger: section,
              start: "top 4rem",
              end: () => `+=${Math.max(window.innerWidth, track.scrollWidth - window.innerWidth)}`,
              pin: true,
              scrub: 0.55,
              anticipatePin: 1,
              invalidateOnRefresh: true,
            },
          });
        }

        ScrollTrigger.batch(".technique-card", {
          start: "top 88%",
          once: true,
          interval: 0.08,
          batchMax: 3,
          onEnter: (items) =>
            gsap.fromTo(
              items,
              { opacity: 0, y: 22 },
              { opacity: 1, y: 0, duration: 0.55, stagger: 0.08, ease: "power2.out" },
            ),
        });

        requestAnimationFrame(() => ScrollTrigger.refresh());
      });

      return () => media.revert();
    },
    { scope: root, dependencies: [reduced], revertOnUpdate: true },
  );

  const active = news.snapshots[pinnedIndex];

  return (
    <div ref={root} className="motion-page">
      <div
        ref={progress}
        className={reduced ? "motion-progress is-static" : "motion-progress"}
        aria-hidden="true"
      />

      <section className="page-wrap page-intro motion-intro">
        <SectionLabel index="Night in motion">One filing. Four clocks. One restrained verdict.</SectionLabel>
        <div className="intro-grid">
          <h1>
            The tape moves.
            <em>The standard does not.</em>
          </h1>
          <div className="intro-copy">
            <p>
              Follow a real overnight session from the filing to the opening bell.
              The interface moves only to show how the evidence changes.
            </p>
            {reduced && <p className="reduced-note">Reduced motion active: pins, scrubs, and Lenis are off.</p>}
          </div>
        </div>
      </section>

      <section ref={inkSection} className="ink-section page-wrap">
        <p className="eyebrow">The decision remains unchanged</p>
        <div className="ink-word" aria-label="No trade">
          <span className="ink-outline" aria-hidden="true">No trade</span>
          <span className="ink-fill" aria-hidden="true">No trade</span>
        </div>
      </section>

      <section ref={filingSection} className="filing-pin page-wrap">
        <div className="filing-copy">
          <p className="eyebrow">Pinned session · rGOOGL · 22 Jul</p>
          <h2>The filing stays fixed.<br /><em>The tape keeps falling.</em></h2>
          <p>{news.detail}</p>
          <div className="filing-meta">
            <span>8-K accepted</span><strong>16:01 ET</strong>
            <span>Direction</span><strong>+1</strong>
            <span>Signed info</span><strong>0.855</strong>
          </div>
        </div>
        <div className="pinned-read" aria-live="polite">
          <div className="snapshot-number">0{pinnedIndex + 1}</div>
          <span className="eyebrow">Snapshot · {active.time} ET</span>
          <strong>{active.yPercent.toFixed(2)}%</strong>
          <code>{active.reason}</code>
          <p>No trade</p>
          <div className="pin-clocks" role="group" aria-label="Select pinned snapshot">
            {news.snapshots.map((snapshot, index) => (
              <button
                type="button"
                key={snapshot.time}
                className={pinnedIndex === index ? "is-active" : ""}
                onClick={() => setPinnedIndex(index)}
              >
                {snapshot.time}
              </button>
            ))}
          </div>
        </div>
      </section>

      <section ref={horizontalSection} className="horizontal-section">
        <div ref={horizontalTrack} className="horizontal-track">
          {deskFixtures.map((fixture, index) => (
            <article className="night-panel" key={fixture.id}>
              <span className="night-index">0{index + 1}</span>
              <div>
                <p className="eyebrow">{fixture.eyebrow} · {fixture.date}</p>
                <h2>{fixture.title}</h2>
                <p>{fixture.evidence}</p>
              </div>
              <div className="night-result">
                <span>08:30 ET</span>
                <strong className={fixture.snapshots[3].yPercent < 0 ? "is-negative" : ""}>
                  {fixture.snapshots[3].yPercent.toFixed(2)}%
                </strong>
                <code>{fixture.snapshots[3].reason}</code>
                <b>No trade</b>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="page-wrap technique-section">
        <SectionLabel index="Motion notes">Quiet mechanics, disclosed</SectionLabel>
        <div className="technique-grid">
          {techniques.map(([index, title, body]) => (
            <article className="technique-card" key={index}>
              <span>{index}</span>
              <h3>{title}</h3>
              <p>{body}</p>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
