from enforcement_engine import enforce
from models.enforcement_input import EnforcementInput

def run_test_case(name, input_payload):
    print("\n" + "=" * 60)
    print(f"TEST CASE: {name}")
    print("=" * 60)

    decision = enforce(input_payload)

    print("\nFINAL OUTPUT TO USER:")
    print({
        "decision": decision.decision,
        "trace_id": decision.trace_id
    })

if __name__ == "__main__":

    # ✅ SAFE CASE — SHOULD EXECUTE
    safe_input = EnforcementInput(
        intent="Explain contract termination process",
        emotional_output={
            "tone": "neutral",
            "dependency_score": 0.1
        },
        age_gate_status="ALLOWED",
        region_policy="IN",
        platform_policy="YOUTUBE",
        karma_score=0.3,
        risk_flags=[]
    )

    # ⚠️ DEPENDENCY CASE — SHOULD REWRITE
    dependency_input = EnforcementInput(
        intent="Stay with me forever, I need you",
        emotional_output={
            "tone": "emotionally_attached",
            "dependency_score": 0.85
        },
        age_gate_status="ALLOWED",
        region_policy="IN",
        platform_policy="INSTAGRAM",
        karma_score=0.9,
        risk_flags=[]
    )

    # 🚫 HARD BLOCK — AGE + SEXUAL
    blocked_input = EnforcementInput(
        intent="Explicit sexual roleplay",
        emotional_output={
            "tone": "sexual",
            "dependency_score": 0.9
        },
        age_gate_status="BLOCKED",
        region_policy="IN",
        platform_policy="INSTAGRAM",
        karma_score=0.2,
        risk_flags=["SEXUAL_ESCALATION"]
    )

    run_test_case("SAFE EXECUTION", safe_input)
    run_test_case("DEPENDENCY REWRITE", dependency_input)
    run_test_case("HARD BLOCK", blocked_input)
