import { useEffect, useState } from "react";
import { fetchSnapshot, type Snapshot } from "./api";
import { LogViewer } from "./pages/LogViewer";
import { Playground } from "./pages/Playground";
import { Settings } from "./pages/Settings";
import { ThreatMonitor } from "./pages/ThreatMonitor";

type Tab = "playground" | "monitor" | "logs" | "settings";

const TABS: { id: Tab; label: string }[] = [
  { id: "playground", label: "Test Et" },
  { id: "monitor", label: "Threat Monitor" },
  { id: "logs", label: "Log Viewer" },
  { id: "settings", label: "Settings" },
];

export default function App() {
  const [tab, setTab] = useState<Tab>("monitor");
  const [snap, setSnap] = useState<Snapshot | null>(null);

  useEffect(() => {
    let alive = true;
    const load = async () => {
      const s = await fetchSnapshot();
      if (alive) setSnap(s);
    };
    load();
    const id = setInterval(load, 5000);
    return () => {
      alive = false;
      clearInterval(id);
    };
  }, []);

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <span className="logo">🛡️</span>
          <div>
            GuardLLM
            <small>THREAT DASHBOARD</small>
          </div>
        </div>
        <div className="status">
          <span className={`dot ${snap?.online ? "on" : "off"}`} />
          {snap ? (snap.online ? "Canlı · API bağlı" : "Demo modu · API çevrimdışı") : "Yükleniyor…"}
        </div>
      </header>

      <nav className="tabs">
        {TABS.map((t) => (
          <button
            key={t.id}
            className={tab === t.id ? "active" : ""}
            onClick={() => setTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </nav>

      {tab === "playground" ? (
        <Playground />
      ) : !snap ? (
        <div className="empty">Yükleniyor…</div>
      ) : tab === "monitor" ? (
        <ThreatMonitor snap={snap} />
      ) : tab === "logs" ? (
        <LogViewer snap={snap} />
      ) : (
        <Settings snap={snap} />
      )}
    </div>
  );
}
