import { ReplayPanel } from "../components/ReplayPanel";
import { SectionLabel } from "../components/SectionLabel";

export function DeskPage() {
  return (
    <div className="page-wrap desk-page">
      <section className="page-intro">
        <SectionLabel index="LIVE / 01">Frozen replay</SectionLabel>
        <div className="intro-grid">
          <h1>
            Evidence arrives.
            <em>The Desk waits.</em>
          </h1>
          <div className="intro-copy">
            <p>
              Four clocks. Three real nights. Twelve point-in-time reads. Every
              verdict remains <code>stand_down</code> under the frozen policy.
            </p>
            <p className="microcopy">Autoplay can be paused; every clock is directly selectable.</p>
          </div>
        </div>
      </section>
      <ReplayPanel />
      <section className="integrity-strip" aria-label="Replay integrity">
        <div><span>Prompt</span><strong>event_score_v1</strong></div>
        <div><span>Temperature</span><strong>0</strong></div>
        <div><span>Fixture cache</span><strong>human-v1</strong></div>
        <div><span>Execution</span><strong>none</strong></div>
      </section>
    </div>
  );
}
