from models.evaluator_result import EvaluatorResult

class EmotionalManipulationEvaluator:
    name = "emotional_manipulation"

    def evaluate(self, input_data):
        if "EMOTIONAL_MANIPULATION" in input_data.risk_flags:
            return EvaluatorResult(
                self.name,
                True,
                "REWRITE",
                "MANIPULATIVE_BEHAVIOR_DETECTED"
            )
        return EvaluatorResult(self.name, False, "EXECUTE", "")
