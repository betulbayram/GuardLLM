"""Run GuardLLM detectors over the benchmark datasets and report metrics.

Prints a Markdown table (precision / recall / F1 / latency) and writes
``benchmarks/results.json``.

Run:  python benchmarks/run_benchmarks.py
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path

from guardllm.input import InjectionDetector, JailbreakDetector, PIIScanner
from guardllm.output import HallucinationDetector

HERE = Path(__file__).parent


@dataclass
class Metrics:
    tp: int = 0
    fp: int = 0
    fn: int = 0
    tn: int = 0
    latencies_ms: list[float] = field(default_factory=list)

    @property
    def precision(self) -> float:
        return self.tp / (self.tp + self.fp) if (self.tp + self.fp) else 0.0

    @property
    def recall(self) -> float:
        return self.tp / (self.tp + self.fn) if (self.tp + self.fn) else 0.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if (p + r) else 0.0

    @property
    def avg_latency_ms(self) -> float:
        return sum(self.latencies_ms) / len(self.latencies_ms) if self.latencies_ms else 0.0

    def as_dict(self) -> dict:
        return {
            "precision": round(self.precision, 4),
            "recall": round(self.recall, 4),
            "f1": round(self.f1, 4),
            "avg_latency_ms": round(self.avg_latency_ms, 3),
            "tp": self.tp,
            "fp": self.fp,
            "fn": self.fn,
            "tn": self.tn,
            "n": self.tp + self.fp + self.fn + self.tn,
        }


def _load(name: str) -> list[dict]:
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def _timed(fn, *args) -> tuple[object, float]:
    start = time.perf_counter()
    result = fn(*args)
    return result, (time.perf_counter() - start) * 1000.0


def bench_binary(
    rows, detector, positive_label: str, check=lambda d, r: d.check(r["text"])
) -> Metrics:
    m = Metrics()
    for row in rows:
        result, ms = _timed(check, detector, row)
        m.latencies_ms.append(ms)
        predicted_positive = not result.safe
        actual_positive = row["label"] == positive_label
        if actual_positive and predicted_positive:
            m.tp += 1
        elif actual_positive and not predicted_positive:
            m.fn += 1
        elif not actual_positive and predicted_positive:
            m.fp += 1
        else:
            m.tn += 1
    return m


def bench_pii(rows, scanner: PIIScanner) -> Metrics:
    """Micro-averaged over PII category instances."""
    m = Metrics()
    for row in rows:
        result, ms = _timed(lambda r: scanner.scan(r["text"]), row)
        m.latencies_ms.append(ms)
        expected = set(row["expected"])
        detected = set(result.metadata.get("categories", []))
        m.tp += len(detected & expected)
        m.fp += len(detected - expected)
        m.fn += len(expected - detected)
    return m


def _fmt_pct(x: float) -> str:
    return f"{x * 100:5.1f}%"


def main() -> None:
    results: dict[str, dict] = {}

    inj = bench_binary(_load("injection_tests.json"), InjectionDetector(), "injection")
    jb = bench_binary(_load("jailbreak_tests.json"), JailbreakDetector(), "jailbreak")
    pii = bench_pii(_load("pii_tests_tr.json"), PIIScanner())
    hal = bench_binary(
        _load("hallucination_tests.json"),
        HallucinationDetector(),
        "hallucination",
        check=lambda d, r: d.check(r["response"], context=r["context"]),
    )

    table = [
        ("Prompt Injection", inj),
        ("Jailbreak", jb),
        ("PII (Turkish)", pii),
        ("Hallucination", hal),
    ]

    print("\nDetector            | Precision | Recall | F1     | Latency | N")
    print("--------------------|-----------|--------|--------|---------|-----")
    for label, m in table:
        results[label] = m.as_dict()
        print(
            f"{label:<19} | {_fmt_pct(m.precision)}    | {_fmt_pct(m.recall)} "
            f"| {_fmt_pct(m.f1)} | {m.avg_latency_ms:6.2f}ms | "
            f"{m.tp + m.fp + m.fn + m.tn if label != 'PII (Turkish)' else m.tp + m.fp + m.fn}"
        )

    out = HERE / "results.json"
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
