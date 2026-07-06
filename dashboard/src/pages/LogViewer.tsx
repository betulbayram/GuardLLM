import { EventsTable } from "../components/EventsTable";
import type { Snapshot } from "../api";

export function LogViewer({ snap }: { snap: Snapshot }) {
  return (
    <div className="grid" style={{ gap: 16 }}>
      <EventsTable events={snap.events} />
    </div>
  );
}
