import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { controlMetrics } from "../data/research";

export function ControlChart() {
  return (
    <div className="control-chart" aria-label="Negative Sharpe ratios for the frozen control">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={controlMetrics} margin={{ top: 12, right: 8, bottom: 4, left: -16 }}>
          <CartesianGrid stroke="#34373d" strokeDasharray="1 5" vertical={false} />
          <XAxis
            dataKey="period"
            tick={{ fill: "#9ca2ac", fontFamily: "IBM Plex Mono", fontSize: 10 }}
            axisLine={{ stroke: "#34373d" }}
            tickLine={false}
          />
          <YAxis
            domain={[-6, 0]}
            ticks={[-6, -4, -2, 0]}
            tick={{ fill: "#777d86", fontFamily: "IBM Plex Mono", fontSize: 10 }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip
            cursor={{ fill: "rgba(232,230,225,0.035)" }}
            contentStyle={{
              background: "#111317",
              border: "1px solid #34373d",
              borderRadius: 0,
              fontFamily: "IBM Plex Mono",
              fontSize: 11,
            }}
            formatter={(value) => [`${Number(value).toFixed(2)}`, "Sharpe"]}
          />
          <Bar dataKey="sharpe" radius={0} maxBarSize={48}>
            {controlMetrics.map((entry) => (
              <Cell key={entry.period} fill="#C9CED6" />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
