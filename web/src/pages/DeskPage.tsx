import { ReplayPanel } from "../components/ReplayPanel";
import { SectionLabel } from "../components/SectionLabel";

export function DeskPage() {
  return (
    <div className="page-wrap desk-page">
      <section className="page-intro">
        <SectionLabel index="Desk replay">Three real nights. Twelve point-in-time reads.</SectionLabel>
        <div className="intro-grid">
          <h1>
            Watch the desk
            <em>refuse a weak signal.</em>
          </h1>
          <div className="intro-copy">
            <p>
              Evidence and price advance together. The frozen policy never sees
              tomorrow’s snapshot and every verdict remains stand down.
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
