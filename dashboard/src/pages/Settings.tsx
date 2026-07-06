import { API_BASE, type Snapshot } from "../api";

export function Settings({ snap }: { snap: Snapshot }) {
  const rows: [string, string][] = [
    ["API adresi", API_BASE],
    ["Bağlantı", snap.online ? "Bağlı" : "Çevrimdışı (demo veri)"],
    ["Alarm eşiği", `${snap.alerts.threshold} tehdit / ${snap.alerts.window_seconds}s`],
    ["Tetiklenen alarm", String(snap.alerts.alerts_fired)],
    ["Aktif dedektörler", "injection, jailbreak, pii, toxicity, hallucination"],
  ];
  return (
    <div className="panel">
      <h3>Ayarlar & Durum</h3>
      {rows.map(([k, v]) => (
        <div className="settings-row" key={k}>
          <span className="k">{k}</span>
          <span className="mono">{v}</span>
        </div>
      ))}
      <p className="muted" style={{ marginTop: 16, fontSize: 13 }}>
        Guard yapılandırması API tarafında <code>configs/default_config.yaml</code> ile
        yönetilir. Bu panel salt-okunur bir izleme arayüzüdür.
      </p>
    </div>
  );
}
