# Demo Kit — ARL v1 (Phase 2)

## Quick Start
- Raj tests:
  - Set PYTHONPATH and run: `pytest -q`
  - Location: `c:\Users\user11\Desktop\Emotional Intelligence\Raj`
- Nilesh full stack:
  - Set env: `API_KEY=localtest`
  - Set PYTHONPATH: `c:\Users\user11\Desktop\Emotional Intelligence\Nilesh`
  - Run: `pytest Nilesh/tests/test_full_stack.py -q`

## Live Gateway (Raj)
- Endpoint: POST `/ai-being/enforce`
- Model: [enforcement_gateway.py](file:///c:/Users/user11/Desktop/Emotional%20Intelligence/Raj/enforcement_gateway.py)
- Behavior:
  - Returns ALLOW / REWRITE / BLOCK
  - Reason constants stable
  - `enforcement_decision_id` generated server-side
  - BLOCK never handed to Akanksha

## Messaging (Nilesh)
- Templates: [arl_messaging.py](file:///c:/Users/user11/Desktop/Emotional%20Intelligence/Nilesh/app/core/arl_messaging.py)
- Tone: Warm, confident, non-dependent
- Cases:
  - BLOCK → Calm refusal
  - REWRITE → Soft redirect
  - ALLOW (VR/Voice) → Reminder

