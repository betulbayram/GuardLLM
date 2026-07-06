import { AlertBanner } from "../components/AlertBanner";
import { EventsTable } from "../components/EventsTable";
import { ThreatPie } from "../components/PieChart";
import { StatCards } from "../components/StatCards";
import { ThreatChart } from "../components/ThreatChart";
import type { Snapshot } from "../api";

export function ThreatMonitor({ snap }: { snap: Snapshot }) {
  return (
    <div className="grid" style={{ gap: 16 }}>
      <AlertBanner alerts={snap.alerts} />
      <StatCards stats={snap.stats} />
      <div className="grid charts">
        <ThreatChart stats={snap.stats} />
        <ThreatPie stats={snap.stats} />
      </div>
      <EventsTable events={snap.events} onlyBlocked />
    </div>
  );
}
