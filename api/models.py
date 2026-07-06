"""Request/response schemas for the GuardLLM API."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field

from guardllm.result import GuardResult


class CheckInputRequest(BaseModel):
    text: str = Field(..., description="User prompt to validate", min_length=1)


class CheckOutputRequest(BaseModel):
    response: str = Field(..., description="LLM response to validate", min_length=1)
    prompt: Optional[str] = Field(None, description="Original prompt (for logging)")
    context: Optional[str] = Field(
        None, description="Grounding context for hallucination checking"
    )


class ScanPIIRequest(BaseModel):
    text: str = Field(..., description="Text to scan for PII", min_length=1)


class KVKKRequest(BaseModel):
    text: str = Field(..., description="Text to check for KVKK compliance", min_length=1)


class GuardResultResponse(BaseModel):
    safe: bool
    threat: Optional[str] = None
    confidence: float
    details: str
    redacted: Optional[str] = None
    detector: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_result(cls, result: GuardResult) -> GuardResultResponse:
        return cls(**result.to_dict())
