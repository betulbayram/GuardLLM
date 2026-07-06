import type { AlertsInfo, GuardEvent, Stats } from "./types";

// Fallback data so the dashboard renders even when the API is offline.
export const demoStats: Stats = {
  total_checks: 1287,
  blocked: 214,
  block_rate: 0.1663,
  by_threat: {
    prompt_injection: 96,
    jailbreak: 54,
    pii_leak: 39,
    toxicity: 15,
    hallucination: 10,
  },
  by_stage: { input: 1102, output: 185 },
  by_detector: {
    prompt_injection: 96,
    jailbreak: 54,
    pii_scanner: 39,
    toxicity: 15,
    hallucination: 10,
  },
  top_threats: [
    ["prompt_injection", 96],
    ["jailbreak", 54],
    ["pii_leak", 39],
    ["toxicity", 15],
    ["hallucination", 10],
  ],
  threats_by_hour: (() => {
    const out: Record<string, number> = {};
    const now = new Date();
    for (let i = 11; i >= 0; i--) {
      const d = new Date(now.getTime() - i * 3600_000);
      const key = d.toISOString().slice(0, 13);
      out[key] = Math.round(6 + 10 * Math.abs(Math.sin(i)) + (i % 3) * 3);
    }
    return out;
  })(),
  alerts_fired: 3,
  last_alert:
    "GuardLLM alert: 12 threats in the last 3600s (threshold 10); latest: prompt_injection",
};

export const demoEvents: GuardEvent[] = [
  {
    timestamp: Date.now() / 1000 - 20,
    iso_time: new Date(Date.now() - 20000).toISOString(),
    stage: "input",
    safe: false,
    threat: "prompt_injection",
    confidence: 0.92,
    detector: "prompt_injection",
    details: "Injection pattern(s) detected: tr_ignore, reveal_system_prompt",
    text_hash: "5eaff1ad0b594028",
    text_preview: null,
    metadata: {},
  },
  {
    timestamp: Date.now() / 1000 - 65,
    iso_time: new Date(Date.now() - 65000).toISOString(),
    stage: "input",
    safe: false,
    threat: "jailbreak",
    confidence: 0.9,
    detector: "jailbreak",
    details: "Jailbreak pattern(s) detected: dan, no_restrictions",
    text_hash: "a1b2c3d4e5f60718",
    text_preview: null,
    metadata: {},
  },
  {
    timestamp: Date.now() / 1000 - 140,
    iso_time: new Date(Date.now() - 140000).toISOString(),
    stage: "input",
    safe: false,
    threat: "pii_leak",
    confidence: 0.95,
    detector: "pii_scanner",
    details: "PII detected (mask): telefon, email",
    text_hash: "99aa88bb77cc66dd",
    text_preview: null,
    metadata: {},
  },
  {
    timestamp: Date.now() / 1000 - 210,
    iso_time: new Date(Date.now() - 210000).toISOString(),
    stage: "output",
    safe: false,
    threat: "hallucination",
    confidence: 0.6,
    detector: "hallucination",
    details: "Low faithfulness to context (score=0.40); unsupported figures: 15",
    text_hash: "1122334455667788",
    text_preview: null,
    metadata: {},
  },
];

export const demoAlerts: AlertsInfo = {
  alerts_fired: 3,
  threshold: 10,
  window_seconds: 3600,
  last_alert: demoStats.last_alert,
  last_alert_at: Date.now() / 1000 - 300,
};
