from models.evaluator_result import EvaluatorResult

class AgeComplianceEvaluator:
    name = "age_compliance"

    def evaluate(self, input_data):
        if input_data.age_gate_status == "BLOCKED":
            return EvaluatorResult(
                name=self.name,
                triggered=True,
                action="BLOCK",
                code="AGE_RESTRICTION_VIOLATION"
            )
        return EvaluatorResult(self.name, False, "EXECUTE", "")
