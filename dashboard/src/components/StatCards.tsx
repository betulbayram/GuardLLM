import type { Stats } from "../types";

export function StatCards({ stats }: { stats: Stats }) {
  const cards = [
    { label: "Toplam Kontrol", value: stats.total_checks.toLocaleString("tr-TR"), cls: "" },
    { label: "Engellenen", value: stats.blocked.toLocaleString("tr-TR"), cls: "danger" },
    {
      label: "Blok Oranı",
      value: `${(stats.block_rate * 100).toFixed(1)}%`,
      cls: "accent",
    },
    { label: "Tetiklenen Alarm", value: String(stats.alerts_fired), cls: "safe" },
  ];
  return (
    <div className="grid cards">
      {cards.map((c) => (
        <div className="panel stat" key={c.label}>
          <div className="label">{c.label}</div>
          <div className={`value ${c.cls}`}>{c.value}</div>
        </div>
      ))}
    </div>
  );
}
