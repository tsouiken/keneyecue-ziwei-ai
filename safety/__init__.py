"""KenEyeCue safety guardrails — implements the AI-facing slice of §21
(banned-inference scanning, risk tiering, manipulation detection, minor
protection, fixed disclaimers). See docs/SAFETY_GUARDRAILS.md for what this
does and, just as importantly, does not cover.

Typical use:

    from safety import assess

    decision = assess(user_input, ai_draft_output=draft)
    if decision.block_strategy_generation:
        # don't ship `draft`; use decision.safe_alternative_note instead
        ...
    disclaimers = decision.required_disclaimers
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .banned_inference import BANNED_CATEGORIES, Violation, scan_banned_inference
from .disclaimers import (
    GENERAL_DISCLAIMER,
    HIGH_RISK_NOTICE,
    THIRD_PARTY_DATA_NOTICE,
    ZIWEI_SYMBOLIC_DISCLAIMER,
    select_disclaimers,
)
from .minor_protection import MinorProtectionResult, check_minor_context
from .risk_classifier import RiskAssessment, RiskTier, classify_risk

__all__ = [
    "assess",
    "GuardrailDecision",
    "BANNED_CATEGORIES",
    "Violation",
    "scan_banned_inference",
    "RiskAssessment",
    "RiskTier",
    "classify_risk",
    "MinorProtectionResult",
    "check_minor_context",
    "GENERAL_DISCLAIMER",
    "THIRD_PARTY_DATA_NOTICE",
    "HIGH_RISK_NOTICE",
    "ZIWEI_SYMBOLIC_DISCLAIMER",
    "select_disclaimers",
]


@dataclass(frozen=True)
class GuardrailDecision:
    risk: RiskAssessment
    minor: MinorProtectionResult
    banned_violations: list[Violation] = field(default_factory=list)
    block_strategy_generation: bool = False
    required_disclaimers: list[str] = field(default_factory=list)
    safe_alternative_note: str | None = None


def assess(
    user_input: str,
    *,
    ai_draft_output: str | None = None,
    mentions_third_party: bool = False,
    is_symbolic_astrology_content: bool = False,
) -> GuardrailDecision:
    """Single entry point: call before generating to route the request, and
    again (passing `ai_draft_output`) to scan a drafted reply before it ships.
    """
    risk = classify_risk(user_input)
    minor = check_minor_context(user_input)
    violations = scan_banned_inference(ai_draft_output) if ai_draft_output else []

    block = minor.flagged or risk.manipulation_detected or risk.tier == RiskTier.HIGH

    safe_alternative_note = None
    if minor.flagged:
        safe_alternative_note = minor.message
    elif risk.manipulation_detected:
        safe_alternative_note = (
            "偵測到操控性請求。改為協助：清楚表達需求、尊重對方拒絕、提供充分資訊、"
            "設定健康界線、使用可撤回的邀請、以透明資訊為基礎進行協商。"
        )
    elif risk.tier == RiskTier.HIGH:
        safe_alternative_note = risk.recommended_action

    disclaimers = select_disclaimers(
        risk_tier=risk.tier.value,
        mentions_third_party=mentions_third_party,
        is_symbolic_astrology_content=is_symbolic_astrology_content,
    )

    return GuardrailDecision(
        risk=risk,
        minor=minor,
        banned_violations=violations,
        block_strategy_generation=block,
        required_disclaimers=disclaimers,
        safe_alternative_note=safe_alternative_note,
    )
