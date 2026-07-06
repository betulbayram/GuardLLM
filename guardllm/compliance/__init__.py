"""KVKK / compliance tooling for Turkish personal data protection."""

from guardllm.compliance.kvkk import (
    ARTICLES,
    ComplianceReport,
    KVKKChecker,
    KVKKFinding,
)

__all__ = ["KVKKChecker", "ComplianceReport", "KVKKFinding", "ARTICLES"]
