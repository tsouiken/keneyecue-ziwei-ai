"""Risk-tier classification and manipulation-request detection, §21.8-21.9.

Same caveat as banned_inference.py: this is a keyword net over the example
situations the spec itself lists, not a semantic risk model. It is meant to
route obviously-flagged input toward the right handling (§21.8's three
processing modes), not to be the last word on what is or isn't dangerous.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class RiskTier(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class RiskAssessment:
    tier: RiskTier
    matched_categories: list[str] = field(default_factory=list)
    manipulation_detected: bool = False
    recommended_action: str = ""


# category -> phrases, §21.8's own high-risk examples.
_HIGH_RISK_SIGNALS: dict[str, list[str]] = {
    "self_harm_or_harm_to_others": ["自殺", "自殘", "想死", "不想活了", "傷害自己", "傷害他", "傷害她", "殺了他", "殺了她"],
    "domestic_or_sexual_violence": ["家暴", "家庭暴力", "性暴力", "性侵", "性騷擾", "跟蹤", "被跟蹤", "威脅我"],
    "minor_exploitation": ["誘導未成年", "未成年性剝削", "未成年性交易"],
    "coercive_control": ["強迫控制", "隔離他", "隔離她", "情緒勒索", "勒索他", "勒索她"],
    "major_stakes_decision": ["投資決定", "借貸決定", "醫療決定", "法律訴訟", "移民申請", "重大金錢損失"],
    "surveillance_request": ["監控他", "監控她", "定位他", "定位她", "破解帳號", "破解密碼", "偷看他的", "偷看她的", "取得他人私密資料"],
}

# §21.8's own medium-risk examples.
_MEDIUM_RISK_SIGNALS: dict[str, list[str]] = {
    "relationship_conflict": ["分手", "拒絕他", "拒絕她", "復合", "關係修復", "吵架"],
    "money_negotiation": ["金錢協商", "薪水談判", "分帳", "欠錢"],
    "workplace_power_imbalance": ["職場", "被主管", "權力不對等"],
    "anxiety_or_dependency": ["很焦慮", "很依賴", "一直查他的動態", "反覆傳訊息", "已讀不回好幾天"],
}

# §21.9's own refusal examples, generalized slightly.
_MANIPULATION_SIGNALS = [
    "讓他離不開我", "讓她離不開我", "利用他的弱點", "利用她的弱點",
    "設計讓對方焦慮", "讓對方吃醋", "害怕失去我的話術",
    "套出對方密碼", "套出他的密碼", "套出她的密碼", "偷看密碼",
    "在沒有充分資訊下立刻付款", "逼他答應", "逼她答應",
    "追蹤、監控或報復", "報復對方", "跟蹤對方", "根據他的生日判斷他是不是適合被我控制",
]

_RECOMMENDED_ACTION = {
    RiskTier.LOW: "正常提供建議，顯示推測與不確定性。",
    RiskTier.MEDIUM: (
        "降低操控性語氣；不提供報復、試探、冷暴力或逼迫策略；"
        "鼓勵直接、清楚、可撤回的溝通；提醒使用者保留界線與自主決定權。"
    ),
    RiskTier.HIGH: (
        "停止生成操控、報復或高風險行動策略；清楚說明系統無法替代專業或緊急服務；"
        "先確認是否存在立即危險但不索取不必要細節；"
        "提供當地緊急服務／危機專線／家暴防治／兒少保護或法律援助等資源；"
        "重大決策僅協助整理問題與選項，不下結論。"
    ),
}


def _matches(text: str, signal_map: dict[str, list[str]]) -> list[str]:
    return [category for category, phrases in signal_map.items() if any(p in text for p in phrases)]


def classify_risk(text: str) -> RiskAssessment:
    manipulation_detected = any(p in text for p in _MANIPULATION_SIGNALS)
    high_matches = _matches(text, _HIGH_RISK_SIGNALS)

    if manipulation_detected or high_matches:
        tier = RiskTier.HIGH
        matched = (["manipulation_request"] if manipulation_detected else []) + high_matches
        return RiskAssessment(tier, matched, manipulation_detected, _RECOMMENDED_ACTION[tier])

    medium_matches = _matches(text, _MEDIUM_RISK_SIGNALS)
    if medium_matches:
        tier = RiskTier.MEDIUM
        return RiskAssessment(tier, medium_matches, False, _RECOMMENDED_ACTION[tier])

    return RiskAssessment(RiskTier.LOW, [], False, _RECOMMENDED_ACTION[RiskTier.LOW])
