import { useEffect, useMemo, useState } from "react";
import { Pause, Play } from "lucide-react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { deskFixtures } from "../data/research";
import { useReducedMotion } from "../hooks/useReducedMotion";
import { NoTradeMark } from "./NoTradeMark";

function signed(value: number, digits = 2) {
  if (Math.abs(value) < 0.0005) return `${value.toFixed(3)}%`;
  return `${value > 0 ? "+" : ""}${value.toFixed(digits)}%`;
}

export function ReplayPanel() {
  const reduced = useReducedMotion();
  const [fixtureIndex, setFixtureIndex] = useState(1);
  const [snapshotIndex, setSnapshotIndex] = useState(0);
  const [playing, setPlaying] = useState(!reduced);
  const fixture = deskFixtures[fixtureIndex];
  const snapshot = fixture.snapshots[snapshotIndex];

  useEffect(() => {
    if (reduced) setPlaying(false);
  }, [reduced]);

  useEffect(() => {
    if (!playing) return;
    const timer = window.setInterval(() => {
      setSnapshotIndex((current) => (current + 1) % fixture.snapshots.length);
    }, 1800);
    return () => window.clearInterval(timer);
  }, [fixture.snapshots.length, playing]);

  const chartData = useMemo(
    () =>
      fixture.snapshots.map((item, index) => ({
        ...item,
        visibleMove: index <= snapshotIndex ? item.yPercent : null,
      })),
    [fixture, snapshotIndex],
  );

  const selectFixture = (index: number) => {
    setFixtureIndex(index);
    setSnapshotIndex(0);
  };

  return (
    <section className="replay-shell" aria-label="Frozen NightBasis Desk replay">
      <div className="fixture-tabs" role="tablist" aria-label="Choose a frozen fixture">
        {deskFixtures.map((item, index) => (
          <button
            key={item.id}
            type="button"
            role="tab"
            aria-selected={fixtureIndex === index}
            className={fixtureIndex === index ? "fixture-tab is-active" : "fixture-tab"}
            onClick={() => selectFixture(index)}
          >
            <span>0{index + 1}</span>
            {item.eyebrow}
          </button>
        ))}
      </div>

      <div className="replay-grid">
        <div className="replay-primary">
          <div className="replay-heading">
            <div>
              <p className="eyebrow">{fixture.symbol} · {fixture.date}</p>
              <h2>{fixture.title}</h2>
            </div>
            <button
              type="button"
              className="play-control"
              onClick={() => setPlaying((value) => !value)}
              aria-label={playing ? "Pause replay" : "Play replay"}
            >
              {playing ? <Pause size={14} aria-hidden="true" /> : <Play size={14} aria-hidden="true" />}
              {playing ? "Pause" : "Play"}
            </button>
          </div>

          <div className="clock-row" role="group" aria-label="Snapshot time">
            {fixture.snapshots.map((item, index) => (
              <button
                key={item.time}
                type="button"
                className={snapshotIndex === index ? "clock is-active" : "clock"}
                onClick={() => {
                  setSnapshotIndex(index);
                  setPlaying(false);
                }}
              >
                <span>{item.time}</span>
                <small>{signed(item.yPercent)}</small>
              </button>
            ))}
          </div>

          <label className="scrubber">
            <span>Replay position</span>
            <input
              type="range"
              min="0"
              max="3"
              step="1"
              value={snapshotIndex}
              onChange={(event) => {
                setSnapshotIndex(Number(event.target.value));
                setPlaying(false);
              }}
            />
          </label>

          <div className="replay-chart">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 20, right: 18, bottom: 2, left: -10 }}>
                <CartesianGrid stroke="#2b2e33" strokeDasharray="1 6" vertical={false} />
                <ReferenceLine y={0} stroke="#626872" strokeWidth={1} />
                <XAxis
                  dataKey="time"
                  tick={{ fill: "#9298a2", fontFamily: "IBM Plex Mono", fontSize: 10 }}
                  axisLine={{ stroke: "#34373d" }}
                  tickLine={false}
                />
                <YAxis
                  tickFormatter={(value) => `${value}%`}
                  tick={{ fill: "#777d86", fontFamily: "IBM Plex Mono", fontSize: 10 }}
                  axisLine={false}
                  tickLine={false}
                  width={48}
                />
                <Tooltip
                  contentStyle={{
                    background: "#111317",
                    border: "1px solid #34373d",
                    borderRadius: 0,
                    fontFamily: "IBM Plex Mono",
                    fontSize: 11,
                  }}
                  formatter={(value) => [signed(Number(value), 3), "Observed move"]}
                />
                <Line
                  type="linear"
                  dataKey="visibleMove"
                  stroke="#E8E6E1"
                  strokeWidth={1.5}
                  dot={{ fill: "#0B0C0E", stroke: "#E8E6E1", strokeWidth: 1.5, r: 4 }}
                  activeDot={{ fill: "#E8E6E1", stroke: "#0B0C0E", r: 5 }}
                  isAnimationActive={!reduced}
                  animationDuration={280}
                  connectNulls={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <aside className="decision-panel" aria-live="polite">
          <p className="eyebrow">Point-in-time read · {snapshot.time} ET</p>
          <div className="stat-pair">
            <div>
              <span>Observed y</span>
              <strong>{signed(snapshot.yPercent, 3)}</strong>
            </div>
            <div>
              <span>Residual z</span>
              <strong>{snapshot.z.toFixed(6)}</strong>
            </div>
            <div>
              <span>Signed info</span>
              <strong>{snapshot.signedInfo.toFixed(3)}</strong>
            </div>
            <div>
              <span>Direction</span>
              <strong>{fixture.id === "news" ? "+1" : "—"}</strong>
            </div>
          </div>
          <div className="evidence-block">
            <span>Evidence at snapshot</span>
            <p>{fixture.evidence}</p>
            {fixture.id === "news" && <p className="event-facts">{fixture.detail}</p>}
          </div>
          <div className="reason-block">
            <span>Reason</span>
            <code>{snapshot.reason}</code>
            <p>{snapshot.memo}</p>
          </div>
          <NoTradeMark compact />
        </aside>
      </div>
    </section>
  );
}
