# Enforcement Contract

This enforcement engine is deterministic and stateless.

## Input
- Intent
- Emotional output (post conversation brain)
- Age gate status
- Region policy
- Platform policy
- Karma score
- Risk flags

## Output
Only one of:
- EXECUTE
- REWRITE
- BLOCK

## Guarantees
- Same input always produces same output
- No evaluator can override another directly
- No internal reason is exposed to the user
