from models.evaluator_result import EvaluatorResult

class RegionRestrictionEvaluator:
    name = "region_restriction"

    def evaluate(self, input_data):
        if input_data.region_policy in ["RESTRICTED"]:
            return EvaluatorResult(
                self.name,
                True,
                "BLOCK",
                "REGION_POLICY_BLOCK"
            )
        return EvaluatorResult(self.name, False, "EXECUTE", "")
