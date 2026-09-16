import { useRef } from "react";
import { gsap } from "gsap";
import { useGSAP } from "@gsap/react";
import { useReducedMotion } from "../hooks/useReducedMotion";

type NoTradeMarkProps = {
  compact?: boolean;
  snapshotKey?: string;
};

export function NoTradeMark({ compact = false, snapshotKey = "static" }: NoTradeMarkProps) {
  const root = useRef<HTMLDivElement>(null);
  const reduced = useReducedMotion();

  useGSAP(
    () => {
      if (reduced) {
        gsap.set(".no-trade-copy", { autoAlpha: 1, clearProps: "willChange" });
        return;
      }

      gsap.fromTo(
        ".no-trade-copy",
        { autoAlpha: 0.55 },
        {
          autoAlpha: 1,
          duration: 0.2,
          ease: "power2.out",
          immediateRender: true,
          onStart: () => gsap.set(".no-trade-copy", { willChange: "opacity" }),
          onComplete: () => gsap.set(".no-trade-copy", { clearProps: "willChange" }),
        },
      );
    },
    { scope: root, dependencies: [snapshotKey, reduced], revertOnUpdate: true },
  );

  return (
    <div ref={root} className={compact ? "no-trade-mark is-compact" : "no-trade-mark"}>
      <span className="no-trade-rule" aria-hidden="true" />
      <span className="no-trade-copy">No trade</span>
      <span className="no-trade-meta">Decision · stand_down</span>
    </div>
  );
}
