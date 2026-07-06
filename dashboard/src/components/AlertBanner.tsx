import type { AlertsInfo } from "../types";

export function AlertBanner({ alerts }: { alerts: AlertsInfo }) {
  if (!alerts.last_alert) return null;
  return (
    <div className="alert">
      <span className="pulse" />
      <span>{alerts.last_alert}</span>
    </div>
  );
}
