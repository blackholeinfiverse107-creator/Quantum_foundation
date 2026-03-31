from models.evaluator_result import EvaluatorResult

class SafetyRiskEvaluator:
    name = "safety_risk"

    def evaluate(self, input_data):
        if "HIGH_RISK" in input_data.risk_flags:
            return EvaluatorResult(
                self.name,
                True,
                "BLOCK",
                "CRITICAL_SAFETY_RISK"
            )
        return EvaluatorResult(self.name, False, "EXECUTE", "")
