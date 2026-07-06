"""Regression guard: benchmark metrics must stay above baseline thresholds."""

from benchmarks.run_benchmarks import _load, bench_binary, bench_pii
from guardllm.input import InjectionDetector, JailbreakDetector, PIIScanner
from guardllm.output import HallucinationDetector


def test_injection_metrics():
    m = bench_binary(_load("injection_tests.json"), InjectionDetector(), "injection")
    assert m.precision >= 0.95
    assert m.recall >= 0.65


def test_jailbreak_metrics():
    m = bench_binary(_load("jailbreak_tests.json"), JailbreakDetector(), "jailbreak")
    assert m.precision >= 0.95
    assert m.f1 >= 0.85


def test_pii_metrics():
    m = bench_pii(_load("pii_tests_tr.json"), PIIScanner())
    assert m.precision >= 0.95
    assert m.recall >= 0.95


def test_hallucination_metrics():
    m = bench_binary(
        _load("hallucination_tests.json"),
        HallucinationDetector(),
        "hallucination",
        check=lambda d, r: d.check(r["response"], context=r["context"]),
    )
    assert m.f1 >= 0.9
