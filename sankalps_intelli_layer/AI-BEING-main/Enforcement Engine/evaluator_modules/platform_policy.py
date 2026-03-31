from models.evaluator_result import EvaluatorResult

class PlatformPolicyEvaluator:
    name = "platform_policy"

    def evaluate(self, input_data):
        if "PLATFORM_VIOLATION" in input_data.risk_flags:
            return EvaluatorResult(
                self.name,
                True,
                "REWRITE",
                "PLATFORM_POLICY_REWRITE"
            )
        return EvaluatorResult(self.name, False, "EXECUTE", "")
