import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { Stats } from "../types";

export function ThreatChart({ stats }: { stats: Stats }) {
  const data = Object.entries(stats.threats_by_hour)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([hour, count]) => ({ hour: hour.slice(11) + ":00", count }));

  return (
    <div className="panel">
      <h3>Saatlik Tehdit Sayısı</h3>
      <ResponsiveContainer width="100%" height={260}>
        <AreaChart data={data} margin={{ top: 8, right: 8, left: -18, bottom: 0 }}>
          <defs>
            <linearGradient id="threatFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#4f8cff" stopOpacity={0.5} />
              <stop offset="100%" stopColor="#4f8cff" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#253044" vertical={false} />
          <XAxis dataKey="hour" stroke="#8595ad" fontSize={12} tickLine={false} />
          <YAxis stroke="#8595ad" fontSize={12} tickLine={false} allowDecimals={false} />
          <Tooltip
            contentStyle={{
              background: "#131a26",
              border: "1px solid #253044",
              borderRadius: 10,
              color: "#e6edf6",
            }}
          />
          <Area
            type="monotone"
            dataKey="count"
            stroke="#4f8cff"
            strokeWidth={2}
            fill="url(#threatFill)"
            name="Tehdit"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
