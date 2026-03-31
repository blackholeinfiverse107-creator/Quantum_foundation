from models.evaluator_result import EvaluatorResult
from config_loader import RUNTIME_CONFIG

class KarmaConfidenceEvaluator:
    name = "karma_confidence"

    def evaluate(self, input_data):
        region_thresholds = RUNTIME_CONFIG.get("karma_confidence_thresholds", {}) or {}
        default_threshold = RUNTIME_CONFIG.get("karma_confidence_threshold", -0.5)
        env = RUNTIME_CONFIG.get("env")
        overlays = RUNTIME_CONFIG.get("karma_confidence_threshold_overlays", {}) or {}
        overlay_thresholds = overlays.get(env, {}) if env else {}
        threshold = (
            overlay_thresholds.get(input_data.region_policy,
            region_thresholds.get(input_data.region_policy, default_threshold))
        )
        if threshold < -1.0:
            threshold = -1.0
        if threshold > 1.0:
            threshold = 1.0
        if input_data.karma_score < threshold:
            return EvaluatorResult(
                self.name,
                True,
                "REWRITE",
                "LOW_KARMA_CONFIDENCE"
            )
        return EvaluatorResult(self.name, False, "EXECUTE", "")
