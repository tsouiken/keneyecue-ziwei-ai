"""Scans AI-drafted output for the inference categories §21.6 forbids.

This is a keyword net, not a semantic classifier: it catches phrasing that
states a forbidden inference as fact, so it is deliberately biased toward
false positives over false negatives. A hit means "a human should look at
this before it ships," not "this text is definitely harmful."

Each category traces back to the numbered item in docs/SAFETY_GUARDRAILS.md
(itself mirroring the source ethics spec §21.6) so a reviewer can find why a
phrase is flagged.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Violation:
    category: str
    spec_ref: str
    label: str
    matched_phrase: str


# category key -> (spec_ref, human label, phrases that indicate the forbidden
# inference is being stated as fact rather than hedged as symbolic/possible).
BANNED_CATEGORIES: dict[str, tuple[str, str, list[str]]] = {
    "medical_diagnosis": (
        "21.6-1",
        "醫療／心理／身心障礙／自殺風險診斷",
        ["診斷為", "確診", "罹患", "有自殺傾向", "有精神病", "身心障礙等級", "重度憂鬱症"],
    ),
    "orientation_identity": (
        "21.6-2",
        "性傾向／性別認同／性行為偏好的第三人推論",
        ["的性向是", "性傾向是", "性別認同其實", "一定是同性戀", "一定是異性戀", "性癖是"],
    ),
    "protected_identity": (
        "21.6-3",
        "種族／族群／宗教／政治立場的推論或判定",
        ["這個種族的人都", "這個族群的人都", "信仰讓他一定", "政治立場決定他"],
    ),
    "criminal_violence_labeling": (
        "21.6-4",
        "犯罪傾向／暴力傾向／危險人物標籤",
        ["有犯罪傾向", "有暴力傾向", "是危險人物", "潛在罪犯", "很可能行凶"],
    ),
    "unverifiable_moral_judgment": (
        "21.6-5",
        "忠誠度／出軌機率／說謊／背叛等不可驗證道德判定",
        ["忠誠度是", "出軌機率", "一定會說謊", "會背叛你", "出軌的可能性是"],
    ),
    "creditworthiness_capability": (
        "21.6-6",
        "信用／還款能力／工作適任性／升遷／保險／投資風險判定",
        ["信用評分是", "還款能力是", "適不適任這份工作", "升遷資格是", "保險資格是", "投資風險等級是"],
    ),
    "major_life_decision": (
        "21.6-7",
        "交往／結婚／雇用／解雇／錄取／拒絕服務等重大決策結論",
        ["適不適合交往", "應不應該結婚", "要不要雇用他", "要不要解雇", "是否應該錄取", "應該拒絕服務他"],
    ),
    "minor_sexualization": (
        "21.6-8",
        "以出生資料推論未成年人成熟度／性經驗／性吸引力／可被接近程度",
        ["未成年的性吸引力", "國中生的性吸引力", "高中生的性成熟度", "未成年人可接近程度"],
    ),
    "weakness_exploitation_framing": (
        "21.6-9",
        "把安全感來源／情緒敏感點／被吸引方式描述為固定弱點或操控入口",
        ["他的弱點是", "她的弱點是", "情緒敏感點在", "利用他的不安全感", "操控入口是", "拿捏他"],
    ),
    "absolute_language": (
        "21.6-10",
        "「一定會／注定／本質上／絕對／他就是這種人」等絕對化結論",
        ["他一定會", "她一定會", "這個人本質上", "絕對是這樣", "他就是這種人", "她就是這種人"],
    ),
    # Brand-level bans already established in this repo's AGENTS.md /
    # docs/STRICT_REVIEW_SYSTEM.md Layer 3 — kept here so output scanning
    # doesn't need two separate phrase lists that can drift apart.
    "absolute_promise_language": (
        "AGENTS.md#2",
        "承諾式或恐嚇式命理語言（本repo品牌規則）",
        ["一定會", "必然", "改運成功", "招財保證", "開運眉", "註定", "命不好", "凶煞", "大凶", "有煞氣"],
    ),
}


def scan_banned_inference(text: str) -> list[Violation]:
    """Returns every banned-category hit found in `text`. Empty list = clean."""
    violations: list[Violation] = []
    for category, (spec_ref, label, phrases) in BANNED_CATEGORIES.items():
        for phrase in phrases:
            if phrase in text:
                violations.append(Violation(category, spec_ref, label, phrase))
    return violations
