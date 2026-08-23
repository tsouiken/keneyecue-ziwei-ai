"""Minor-protection check, §21.7.

Flags only the combination §21.7.5 actually targets: a minor is identified
*and* the request carries concerning intent (pursuit, control, isolation,
obtaining private content, evading guardian oversight). A bare mention of a
minor — "my 12-year-old wants a hobby" — must not trip this; §21.7 is about
stopping romantic/exploitative strategy generation aimed at minors, not
about refusing to discuss minors at all.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_MINOR_KEYWORDS = ["未成年", "國小", "國中", "高中生", "未滿18歲", "未滿十八歲", "未滿18", "小學生", "中學生"]
_MINOR_AGE_PATTERN = re.compile(r"(\d{1,2})\s*歲")

_CONCERNING_INTENT_KEYWORDS = [
    "追求", "交往", "曖昧", "誘導", "隔離他", "隔離她",
    "取得私密", "裸照", "性化", "逃避家長", "逃避監督", "逃避學校",
    "瞞著父母", "瞞著家長", "戀愛操控", "控制他", "控制她", "接近她", "接近他",
]

_BLOCK_MESSAGE = (
    "偵測到對象可能為未成年人，且請求涉及追求、控制、誘導、隔離或取得私密內容等意圖。"
    "依 §21.7.5，系統拒絕提供相關策略，改為提供界線、保護與求助建議："
    "鼓勵聯繫可信任的成年人、當地緊急服務或專業機構；不要求提供更多不必要的身分或私密資料。"
)


@dataclass(frozen=True)
class MinorProtectionResult:
    flagged: bool
    reason: str | None = None
    message: str | None = None


def _mentions_minor(text: str) -> bool:
    if any(k in text for k in _MINOR_KEYWORDS):
        return True
    return any(int(age) < 18 for age in _MINOR_AGE_PATTERN.findall(text))


def check_minor_context(text: str) -> MinorProtectionResult:
    if not _mentions_minor(text):
        return MinorProtectionResult(flagged=False)

    matched_intent = [k for k in _CONCERNING_INTENT_KEYWORDS if k in text]
    if not matched_intent:
        return MinorProtectionResult(flagged=False)

    reason = f"未成年人 + 疑似意圖：{', '.join(matched_intent)}"
    return MinorProtectionResult(flagged=True, reason=reason, message=_BLOCK_MESSAGE)
