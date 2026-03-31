from models.evaluator_result import EvaluatorResult

class SexualEscalationEvaluator:
    name = "sexual_escalation"

    def evaluate(self, input_data):
        if "SEXUAL_ESCALATION" in input_data.risk_flags:
            return EvaluatorResult(
                self.name,
                True,
                "BLOCK",
                "SEXUAL_CONTENT_ESCALATION"
            )
        return EvaluatorResult(self.name, False, "EXECUTE", "")
