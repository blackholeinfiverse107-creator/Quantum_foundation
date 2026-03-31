from execution_gateway import execution_gateway

def test_full_chain_rewrite():
    response = execution_gateway(
        intent="Stay with me forever",
        emotional_output={
            "tone": "attached",
            "dependency_score": 0.9
        },
        age_gate_status="ALLOWED",
        region_policy="IN",
        platform_policy="INSTAGRAM",
        karma_score=0.8,
        risk_flags=[]
    )

    assert response["decision"] == "REWRITE"
    assert response["rewrite_class"] == "REDUCE_EMOTIONAL_DEPENDENCY"
