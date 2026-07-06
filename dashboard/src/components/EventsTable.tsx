import type { GuardEvent } from "../types";

function timeAgo(ts: number): string {
  const s = Math.max(0, Math.floor(Date.now() / 1000 - ts));
  if (s < 60) return `${s}sn önce`;
  if (s < 3600) return `${Math.floor(s / 60)}dk önce`;
  return `${Math.floor(s / 3600)}sa önce`;
}

export function EventsTable({ events, onlyBlocked = false }: { events: GuardEvent[]; onlyBlocked?: boolean }) {
  const rows = onlyBlocked ? events.filter((e) => !e.safe) : events;
  const ordered = [...rows].reverse();

  return (
    <div className="panel">
      <h3>{onlyBlocked ? "Son Engellenen İstekler" : "Olay Kaydı"}</h3>
      {ordered.length === 0 ? (
        <div className="empty">Kayıt yok</div>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Zaman</th>
              <th>Aşama</th>
              <th>Durum</th>
              <th>Güven</th>
              <th>Detay</th>
              <th>Hash</th>
            </tr>
          </thead>
          <tbody>
            {ordered.map((e, i) => (
              <tr key={`${e.text_hash}-${i}`}>
                <td className="muted">{timeAgo(e.timestamp)}</td>
                <td className="muted">{e.stage}</td>
                <td>
                  <span className={`badge ${e.safe ? "safe" : e.threat ?? ""}`}>
                    {e.safe ? "safe" : e.threat}
                  </span>
                </td>
                <td className="mono">{(e.confidence * 100).toFixed(0)}%</td>
                <td>{e.details}</td>
                <td className="mono">{e.text_hash ?? "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
