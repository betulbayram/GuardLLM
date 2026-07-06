import { demoAlerts, demoEvents, demoStats } from "./demoData";
import type {
  AlertsInfo,
  GuardCheckResult,
  GuardEvent,
  KVKKReport,
  Stats,
} from "./types";

const BASE = (import.meta.env.VITE_API_URL as string) || "http://localhost:8000";

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { headers: { Accept: "application/json" } });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return (await res.json()) as T;
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    let detail = `${res.status} ${res.statusText}`;
    try {
      const data = await res.json();
      if (data?.detail) detail = JSON.stringify(data.detail);
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  return (await res.json()) as T;
}

// --- Playground calls (require the API to be running) --------------------- //
export const checkInput = (text: string) =>
  post<GuardCheckResult>("/check/input", { text });

export const checkOutput = (response: string, context?: string) =>
  post<GuardCheckResult>("/check/output", { response, context: context || null });

export const scanPII = (text: string) =>
  post<GuardCheckResult>("/scan/pii", { text });

export const checkKVKK = (text: string) =>
  post<KVKKReport>("/compliance/kvkk", { text });

export interface Snapshot {
  stats: Stats;
  events: GuardEvent[];
  alerts: AlertsInfo;
  online: boolean;
}

/** Fetch everything the dashboard needs; fall back to demo data if offline. */
export async function fetchSnapshot(): Promise<Snapshot> {
  try {
    const [stats, events, alerts] = await Promise.all([
      get<Stats>("/monitor/stats"),
      get<GuardEvent[]>("/monitor/recent?n=50"),
      get<AlertsInfo>("/monitor/alerts"),
    ]);
    return { stats, events, alerts, online: true };
  } catch {
    return {
      stats: demoStats,
      events: demoEvents,
      alerts: demoAlerts,
      online: false,
    };
  }
}

export { BASE as API_BASE };
