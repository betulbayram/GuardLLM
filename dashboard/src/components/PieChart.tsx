import { Cell, Legend, Pie, PieChart as RPieChart, ResponsiveContainer, Tooltip } from "recharts";
import type { Stats } from "../types";

const COLORS: Record<string, string> = {
  prompt_injection: "#ff6b6b",
  jailbreak: "#ffa94d",
  pii_leak: "#4dd4c4",
  toxicity: "#b98bff",
  hallucination: "#6ba8ff",
};

export function ThreatPie({ stats }: { stats: Stats }) {
  const data = Object.entries(stats.by_threat).map(([name, value]) => ({ name, value }));

  return (
    <div className="panel">
      <h3>Tehdit Türü Dağılımı</h3>
      {data.length === 0 ? (
        <div className="empty">Henüz tehdit yok 🎉</div>
      ) : (
        <ResponsiveContainer width="100%" height={260}>
          <RPieChart>
            <Pie
              data={data}
              dataKey="value"
              nameKey="name"
              innerRadius={55}
              outerRadius={90}
              paddingAngle={3}
            >
              {data.map((d) => (
                <Cell key={d.name} fill={COLORS[d.name] || "#4f8cff"} stroke="#0b0f17" />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                background: "#131a26",
                border: "1px solid #253044",
                borderRadius: 10,
                color: "#e6edf6",
              }}
            />
            <Legend
              formatter={(v: string) => <span style={{ color: "#8595ad", fontSize: 12 }}>{v}</span>}
            />
          </RPieChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
