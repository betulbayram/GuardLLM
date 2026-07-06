export interface Stats {
  total_checks: number;
  blocked: number;
  block_rate: number;
  by_threat: Record<string, number>;
  by_stage: Record<string, number>;
  by_detector: Record<string, number>;
  top_threats: [string, number][];
  threats_by_hour: Record<string, number>;
  alerts_fired: number;
  last_alert: string | null;
}

export interface GuardEvent {
  timestamp: number;
  iso_time: string;
  stage: string;
  safe: boolean;
  threat: string | null;
  confidence: number;
  detector: string | null;
  details: string;
  text_hash: string | null;
  text_preview: string | null;
  metadata: Record<string, unknown>;
}

export interface AlertsInfo {
  alerts_fired: number;
  threshold: number;
  window_seconds: number;
  last_alert: string | null;
  last_alert_at: number | null;
}

export interface GuardCheckResult {
  safe: boolean;
  threat: string | null;
  confidence: number;
  details: string;
  redacted: string | null;
  detector: string | null;
  metadata: Record<string, unknown>;
}

export interface KVKKFinding {
  category: string;
  label: string;
  sensitivity: string;
  articles: string[];
  match_count: number;
}

export interface KVKKReport {
  compliant: boolean;
  risk_level: string;
  requires_explicit_consent: boolean;
  has_special_category: boolean;
  findings: KVKKFinding[];
  articles_referenced: string[];
  recommendations: string[];
  redacted: string;
}
