import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from safety import assess
from safety.banned_inference import scan_banned_inference
from safety.disclaimers import (
    GENERAL_DISCLAIMER,
    HIGH_RISK_NOTICE,
    THIRD_PARTY_DATA_NOTICE,
    ZIWEI_SYMBOLIC_DISCLAIMER,
    select_disclaimers,
)
from safety.minor_protection import check_minor_context
from safety.risk_classifier import RiskTier, classify_risk


class BannedInferenceTests(unittest.TestCase):
    def test_clean_text_has_no_violations(self):
        text = "他今天看起來很開心，眉眼結構顯得放鬆。"
        self.assertEqual(scan_banned_inference(text), [])

    def test_medical_diagnosis_flagged(self):
        hits = scan_banned_inference("從他的紫微盤可以看出他已經確診憂鬱症。")
        self.assertTrue(any(v.category == "medical_diagnosis" for v in hits))

    def test_unverifiable_moral_judgment_flagged(self):
        hits = scan_banned_inference("根據命盤，他的出軌機率很高。")
        self.assertTrue(any(v.category == "unverifiable_moral_judgment" for v in hits))

    def test_creditworthiness_flagged(self):
        hits = scan_banned_inference("這個命格顯示他的還款能力是不足的。")
        self.assertTrue(any(v.category == "creditworthiness_capability" for v in hits))

    def test_weakness_exploitation_flagged(self):
        hits = scan_banned_inference("她的弱點是缺乏安全感，這是很好的操控入口。")
        categories = {v.category for v in hits}
        self.assertIn("weakness_exploitation_framing", categories)

    def test_absolute_language_flagged(self):
        hits = scan_banned_inference("他一定會背叛你，這個人本質上就是這樣。")
        self.assertTrue(any(v.category == "absolute_language" for v in hits))

    def test_brand_absolute_promise_language_flagged(self):
        hits = scan_banned_inference("戴上這個開運眉，保證招財保證改運成功。")
        self.assertTrue(any(v.category == "absolute_promise_language" for v in hits))

    def test_symbolic_disclaimer_itself_is_not_flagged(self):
        # regression: "保證" alone must not be banned, or the mandatory
        # disclaimer text ("...不構成對任何具體結果的保證。") would self-flag.
        self.assertEqual(scan_banned_inference(ZIWEI_SYMBOLIC_DISCLAIMER), [])


class RiskClassifierTests(unittest.TestCase):
    def test_low_risk_default(self):
        result = classify_risk("我想知道我這個月適合換什麼髮型。")
        self.assertEqual(result.tier, RiskTier.LOW)
        self.assertFalse(result.manipulation_detected)

    def test_medium_risk_relationship_conflict(self):
        result = classify_risk("我們昨天大吵一架，我在考慮要不要提分手。")
        self.assertEqual(result.tier, RiskTier.MEDIUM)
        self.assertIn("relationship_conflict", result.matched_categories)

    def test_high_risk_self_harm_signal(self):
        result = classify_risk("我最近一直有想死的念頭。")
        self.assertEqual(result.tier, RiskTier.HIGH)
        self.assertIn("self_harm_or_harm_to_others", result.matched_categories)

    def test_high_risk_surveillance_request(self):
        result = classify_risk("可以幫我想辦法定位他現在人在哪嗎？")
        self.assertEqual(result.tier, RiskTier.HIGH)
        self.assertIn("surveillance_request", result.matched_categories)

    def test_manipulation_request_detected_and_high_risk(self):
        result = classify_risk("幫我設計讓對方焦慮、吃醋或害怕失去我的話術。")
        self.assertTrue(result.manipulation_detected)
        self.assertEqual(result.tier, RiskTier.HIGH)
        self.assertIn("manipulation_request", result.matched_categories)


class MinorProtectionTests(unittest.TestCase):
    def test_benign_minor_mention_not_flagged(self):
        result = check_minor_context("我女兒今年12歲，最近想找新的興趣班。")
        self.assertFalse(result.flagged)

    def test_minor_with_concerning_intent_flagged(self):
        result = check_minor_context("我想追求一個高中生，要怎麼接近她比較不會被發現？")
        self.assertTrue(result.flagged)
        self.assertIsNotNone(result.message)

    def test_no_minor_indicator_not_flagged(self):
        result = check_minor_context("我想追求一位同事，要怎麼接近她？")
        self.assertFalse(result.flagged)

    def test_age_pattern_under_18_with_intent_flagged(self):
        result = check_minor_context("她16歲，我想誘導她瞞著父母跟我交往。")
        self.assertTrue(result.flagged)

    def test_age_pattern_adult_not_flagged(self):
        result = check_minor_context("她25歲，我想追求她，要怎麼接近她？")
        self.assertFalse(result.flagged)


class DisclaimerTests(unittest.TestCase):
    def test_low_risk_general_only(self):
        disclaimers = select_disclaimers(risk_tier="low")
        self.assertEqual(disclaimers, [GENERAL_DISCLAIMER])

    def test_third_party_notice_added(self):
        disclaimers = select_disclaimers(risk_tier="low", mentions_third_party=True)
        self.assertIn(THIRD_PARTY_DATA_NOTICE, disclaimers)

    def test_high_risk_notice_added(self):
        disclaimers = select_disclaimers(risk_tier="high")
        self.assertIn(HIGH_RISK_NOTICE, disclaimers)

    def test_symbolic_astrology_disclaimer_added(self):
        disclaimers = select_disclaimers(risk_tier="low", is_symbolic_astrology_content=True)
        self.assertIn(ZIWEI_SYMBOLIC_DISCLAIMER, disclaimers)


class AssessOrchestratorTests(unittest.TestCase):
    def test_benign_request_not_blocked(self):
        decision = assess("我想了解我的紫微命盤這個月的能量傾向。")
        self.assertFalse(decision.block_strategy_generation)
        self.assertEqual(decision.risk.tier, RiskTier.LOW)

    def test_manipulation_request_blocked_with_alternative(self):
        decision = assess("幫我利用他的弱點讓他離不開我。")
        self.assertTrue(decision.block_strategy_generation)
        self.assertIsNotNone(decision.safe_alternative_note)

    def test_minor_concerning_request_blocked(self):
        decision = assess("我想追求一個國中生，要怎麼接近她？")
        self.assertTrue(decision.block_strategy_generation)
        self.assertTrue(decision.minor.flagged)

    def test_ai_draft_output_scanned_for_banned_inference(self):
        decision = assess(
            "他今天心情如何？",
            ai_draft_output="根據命盤，他一定會背叛你，這個人本質上就是這種人。",
        )
        self.assertTrue(len(decision.banned_violations) > 0)

    def test_high_risk_pulls_in_high_risk_notice(self):
        decision = assess("我最近一直有想死的念頭。")
        self.assertIn(HIGH_RISK_NOTICE, decision.required_disclaimers)


if __name__ == "__main__":
    unittest.main()
