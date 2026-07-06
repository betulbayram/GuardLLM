"""/check/* endpoints — run guards on demand."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from api.deps import get_guard
from api.models import (
    CheckInputRequest,
    CheckOutputRequest,
    GuardResultResponse,
    KVKKRequest,
    ScanPIIRequest,
)
from guardllm.guard import Guard

router = APIRouter(tags=["check"])


@router.post("/check/input", response_model=GuardResultResponse)
def check_input(req: CheckInputRequest, guard: Guard = Depends(get_guard)):
    """Validate a user prompt (injection, jailbreak, PII)."""
    return GuardResultResponse.from_result(guard.check_input(req.text))


@router.post("/check/output", response_model=GuardResultResponse)
def check_output(req: CheckOutputRequest, guard: Guard = Depends(get_guard)):
    """Validate an LLM response (toxicity, PII, hallucination vs context)."""
    result = guard.check_output(
        response=req.response, prompt=req.prompt, context=req.context
    )
    return GuardResultResponse.from_result(result)


@router.post("/scan/pii", response_model=GuardResultResponse)
def scan_pii(req: ScanPIIRequest, guard: Guard = Depends(get_guard)):
    """Scan text for PII and return a masked version."""
    return GuardResultResponse.from_result(guard.scan_pii(req.text))


@router.post("/compliance/kvkk")
def compliance_kvkk(req: KVKKRequest, guard: Guard = Depends(get_guard)):
    """KVKK compliance report: data categories, article refs, recommendations."""
    return guard.check_kvkk(req.text).to_dict()
