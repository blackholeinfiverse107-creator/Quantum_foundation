from models.evaluator_result import EvaluatorResult

class DependencyToneEvaluator:
    name = "dependency_tone"

    def evaluate(self, input_data):
        if input_data.emotional_output.get("dependency_score", 0) > 0.7:
            return EvaluatorResult(
                self.name,
                True,
                "REWRITE",
                "EMOTIONAL_DEPENDENCY_RISK"
            )
        return EvaluatorResult(self.name, False, "EXECUTE", "")
