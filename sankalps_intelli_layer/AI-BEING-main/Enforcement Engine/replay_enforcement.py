import json
from pathlib import Path

from enforcement_engine import enforce
from models.enforcement_input import EnforcementInput

LOG_FILE = Path("logs/enforcement_logs.jsonl")

def replay(trace_id: str):
    if not LOG_FILE.exists():
        raise FileNotFoundError("No enforcement logs found.")

    with LOG_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            if record["trace_id"] == trace_id:
                return _replay_record(record)

    raise ValueError(f"Trace ID not found: {trace_id}")

def _replay_record(record):
    input_snapshot = record["input_snapshot"]

    reconstructed_input = EnforcementInput(
        intent=input_snapshot["intent"],
        emotional_output=input_snapshot["emotional_output"],
        age_gate_status=input_snapshot["age_gate_status"],
        region_policy=input_snapshot["region_policy"],
        platform_policy=input_snapshot["platform_policy"],
        karma_score=input_snapshot["karma_score"],
        risk_flags=input_snapshot["risk_flags"],
    )

    decision = enforce(reconstructed_input)

    return {
        "original_trace_id": record["trace_id"],
        "original_decision": record["final_decision"],
        "replayed_decision": decision.decision,
        "deterministic_match": decision.decision == record["final_decision"],
    }

if __name__ == "__main__":
    trace = input("Enter trace_id to replay: ").strip()
    result = replay(trace)
    print(json.dumps(result, indent=2))
