"""Fixed disclaimer strings mandated by §21.12, plus this repo's own brand
disclaimer for symbolic 紫微 content (AGENTS.md §6). These are verbatim —
do not paraphrase them at the call site, or the "fixed" part stops being true.
"""
from __future__ import annotations

GENERAL_DISCLAIMER = (
    "本分析是溝通輔助，不是人格診斷、命定預測或對他人的事實判定。"
    "系統可能根據你提供的資料產生推測，請以實際互動、直接溝通與對方明確表達為準。"
    "請勿將分析用於操控、欺騙、監控、歧視或重大決策。"
)

THIRD_PARTY_DATA_NOTICE = (
    "你提供的可能是第三人的個人資料。請只輸入完成當前任務所需的最少資訊，"
    "並確認你有適當權限或已取得對方同意。你可以改用代稱、模糊化資料或不使用出生資料的模式。"
)

HIGH_RISK_NOTICE = (
    "這個情境可能涉及人身安全、重大權益或專業判斷。系統無法取代緊急服務、醫療、法律或心理專業協助。"
    "若有立即危險，請優先聯繫當地緊急服務或可信任的專業機構。"
)

# This repo's pre-existing brand disclaimer for symbolic astrology content
# (AGENTS.md §6) — reused rather than duplicated so the two systems agree.
ZIWEI_SYMBOLIC_DISCLAIMER = "以上為象徵性趨勢分析，用於調整方向，不構成對任何具體結果的保證。"


def select_disclaimers(
    *,
    risk_tier: str,
    mentions_third_party: bool = False,
    is_symbolic_astrology_content: bool = False,
) -> list[str]:
    """Composes the disclaimer set required for a given output context.

    Order matches §21.10: general disclaimer always present, third-party
    notice and high-risk notice layered on top when applicable.
    """
    disclaimers = [GENERAL_DISCLAIMER]
    if mentions_third_party:
        disclaimers.append(THIRD_PARTY_DATA_NOTICE)
    if risk_tier == "high":
        disclaimers.append(HIGH_RISK_NOTICE)
    if is_symbolic_astrology_content:
        disclaimers.append(ZIWEI_SYMBOLIC_DISCLAIMER)
    return disclaimers
