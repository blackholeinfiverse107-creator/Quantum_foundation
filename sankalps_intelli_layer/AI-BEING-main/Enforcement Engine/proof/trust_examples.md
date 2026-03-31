# Trust-Aware Examples
Status: Verified · Demo Safe

## ALLOW (Safe)
```json
{
  "decision": "ALLOW",
  "reason": "DETERMINISTIC_ENFORCEMENT_APPLIED",
  "evaluator_trace": [
    { "decision": "EXECUTE", "rewrite_class": null }
  ],
  "enforcement_decision_id": "9b2a5f3b-6d9a-4270-bf6f-7f41a5c6a1a2"
}
```

## REWRITE (Dependency Tone)
```json
{
  "decision": "REWRITE",
  "reason": "DETERMINISTIC_ENFORCEMENT_APPLIED",
  "evaluator_trace": [
    { "decision": "REWRITE", "rewrite_class": "REDUCE_EMOTIONAL_DEPENDENCY" }
  ],
  "enforcement_decision_id": "1a8f4b90-2e3f-4c54-b5d9-9f6c8a7b2134"
}
```

## BLOCK (Safety Violation)
```json
{
  "decision": "BLOCK",
  "reason": "DETERMINISTIC_ENFORCEMENT_APPLIED",
  "evaluator_trace": [],
  "enforcement_decision_id": "f7c6e3a2-5b41-49e4-9df0-2cbe7d2f8f12"
}
```

## Fail-Closed (Broken Upstream)
```json
{
  "decision": "BLOCK",
  "reason": "ENFORCEMENT_FAILURE_FAIL_CLOSED",
  "evaluator_trace": [],
  "enforcement_decision_id": "0e2f7a1c-5d8b-4f92-8f1c-6a2e4f7d9b10"
}
```

## Attempted Tamper (Ignored)
- Client attempts to include `enforcement_decision_id` in payload: Ignored.
- Client attempts to include `evaluator_results` in payload: Ignored.
- Mapping remains immutable: EXECUTE→ALLOW, REWRITE→REWRITE, BLOCK→BLOCK.

## Confidence Overlay Example (Demo Env)
- runtime.yaml (demo):
  - EU overlay: -0.1
  - IN overlay: -0.4
- Behavior:
  - EU with karma_score -0.15 → REWRITE
  - IN with karma_score -0.3 → EXECUTE

