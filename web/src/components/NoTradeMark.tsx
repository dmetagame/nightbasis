type NoTradeMarkProps = {
  compact?: boolean;
};

export function NoTradeMark({ compact = false }: NoTradeMarkProps) {
  return (
    <div className={compact ? "no-trade-mark is-compact" : "no-trade-mark"}>
      <span className="no-trade-rule" aria-hidden="true" />
      <span className="no-trade-copy">No trade</span>
      <span className="no-trade-meta">Decision · stand_down</span>
    </div>
  );
}
