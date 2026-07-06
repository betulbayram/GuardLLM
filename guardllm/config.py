"""Configuration models for GuardLLM.

Config can be built in code or loaded from a YAML file that mirrors the
structure documented in ``configs/default_config.yaml``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

import yaml
from pydantic import BaseModel, Field


class DetectorConfig(BaseModel):
    """Base settings shared by every detector."""

    enabled: bool = True
    threshold: float = Field(default=0.8, ge=0.0, le=1.0)


class InjectionConfig(DetectorConfig):
    languages: list[str] = Field(default_factory=lambda: ["tr", "en"])


class JailbreakConfig(DetectorConfig):
    threshold: float = Field(default=0.8, ge=0.0, le=1.0)


class PIIConfig(DetectorConfig):
    categories: list[str] = Field(
        default_factory=lambda: [
            "tc_kimlik",
            "telefon",
            "email",
            "iban",
            "kredi_karti",
        ]
    )
    action: str = Field(default="mask")  # mask | block | warn


class HallucinationConfig(DetectorConfig):
    threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    method: str = Field(default="nli")  # nli | llm_judge


class ToxicityConfig(DetectorConfig):
    threshold: float = Field(default=0.8, ge=0.0, le=1.0)


class TopicConfig(DetectorConfig):
    enabled: bool = False  # app-specific; opt-in
    mode: str = "blocklist"  # blocklist | allowlist
    # topic name -> keywords that define the topic
    topics: dict[str, list[str]] = Field(default_factory=dict)
    blocked: list[str] = Field(default_factory=list)  # blocklist mode
    allowed: list[str] = Field(default_factory=list)  # allowlist mode
    min_keywords: int = 1  # keyword hits needed to consider a topic matched


class InputGuardConfig(BaseModel):
    prompt_injection: InjectionConfig = Field(default_factory=InjectionConfig)
    jailbreak: JailbreakConfig = Field(default_factory=JailbreakConfig)
    pii_scanner: PIIConfig = Field(default_factory=PIIConfig)
    topic_restrictor: TopicConfig = Field(default_factory=TopicConfig)


class OutputGuardConfig(BaseModel):
    hallucination: HallucinationConfig = Field(default_factory=HallucinationConfig)
    toxicity: ToxicityConfig = Field(default_factory=ToxicityConfig)
    pii_redactor: PIIConfig = Field(default_factory=PIIConfig)


class MonitorConfig(BaseModel):
    enabled: bool = False
    log_to: str = "stdout"  # postgresql | file | stdout | null
    log_file: Optional[str] = None  # path used when log_to == "file"
    dsn: Optional[str] = None  # connection string when log_to == "postgresql"
    alert_threshold: int = 10  # threats within the window before alerting
    alert_window_seconds: int = 3600  # sliding window for alert_threshold
    store_text: bool = False  # store a text preview on events (may contain PII)


class GuardConfig(BaseModel):
    """Top-level configuration for a :class:`~guardllm.guard.Guard`."""

    input: InputGuardConfig = Field(default_factory=InputGuardConfig)
    output: OutputGuardConfig = Field(default_factory=OutputGuardConfig)
    monitor: MonitorConfig = Field(default_factory=MonitorConfig)

    @classmethod
    def from_yaml(cls, path: Union[str, Path]) -> GuardConfig:
        """Load configuration from a YAML file.

        The YAML may optionally nest everything under a top-level ``guards:``
        key (as shown in the docs); both layouts are accepted.
        """
        path = Path(path)
        with path.open("r", encoding="utf-8") as fh:
            raw = yaml.safe_load(fh) or {}
        if "guards" in raw:
            raw = raw["guards"]
        return cls.model_validate(raw)

    @classmethod
    def default(cls) -> GuardConfig:
        """Return the built-in default configuration."""
        return cls()


def load_config(config: Optional[Union[str, Path, GuardConfig]] = None) -> GuardConfig:
    """Coerce various inputs into a :class:`GuardConfig`.

    Accepts ``None`` (defaults), a path to a YAML file, or an existing
    :class:`GuardConfig` instance.
    """
    if config is None:
        return GuardConfig.default()
    if isinstance(config, GuardConfig):
        return config
    return GuardConfig.from_yaml(config)
