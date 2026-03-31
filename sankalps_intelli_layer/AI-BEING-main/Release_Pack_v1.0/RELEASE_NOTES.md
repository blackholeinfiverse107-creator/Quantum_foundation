# Release Pack v1.0 - Adaptive Response Layer (ARL)

**Release Date:** 2026-01-14
**Version:** ARL v1.0.0
**Enforcement Engine Version:** 1.0.0

## 📦 Contents

### 1. Contracts (`/contracts`)
- `enforcement_contract.md`: The core rules of engagement.
- `enforcement_contract_v2.md`: Updated mappings for v1.0 release.
- `failure_resilience_matrix.json`: Definition of fail-closed behaviors.
- `trust_alignment_v2.md`: Trust and safety guarantees.

### 2. Proofs (`/proofs`)
- `e2e_run_logs_day6.txt`: End-to-End integration test logs demonstrating normal, block, rewrite, and warning flows.
- `chaos_pass_report.txt` (if available): Fuzz testing results.
- `trace_map.json` (if available): Decision trace examples.

### 3. Demo Kit (`/demo_kit`)
To run the demo, execute the E2E integration tests:

```bash
cd "Backend Stability Spine"
$env:API_KEY="localtest"
pytest tests/test_e2e_integration.py
```

## 🚀 Key Features

- **Fail-Closed Enforcement**: Raj unavailability maps to BLOCK.
- **Karma-Aware Tone**: User karma (-1.0 to 1.0) adjusts response tone (Calm/Steady/Neutral).
- **VR/Voice Safety**: Automatic warnings for immersive contexts.
- **Privacy-First**: No internal IDs or policy names leaked to frontend.

## 🛑 Known Limitations

- "DeprecationWarning" logs from Google Generative AI libraries (harmless for now).
- Local-only execution (requires local `uvicorn` server for full stack).

---
*Signed off by Pair Programmer*
