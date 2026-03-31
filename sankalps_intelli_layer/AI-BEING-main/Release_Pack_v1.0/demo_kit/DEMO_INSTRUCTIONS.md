# ARL Demo Kit Instructions

## Prerequisites
- Python 3.10+
- Dependencies installed (`pip install -r requirements.txt` in Backend Stability Spine)

## How to Run the Demo

The demo is automated via the E2E test suite which exercises the full stack (Backend -> Enforcement -> ARL -> Frontend).

1. Open a PowerShell terminal.
2. Navigate to the backend directory:
   ```powershell
   cd "c:\Users\user11\Desktop\Emotional Intelligence\Backend Stability Spine"
   ```
3. Set the test API key:
   ```powershell
   $env:API_KEY="localtest"
   ```
4. Run the E2E tests:
   ```powershell
   pytest tests/test_e2e_integration.py -v
   ```

## Interpreting Results
- **PASSED**: The pipeline is functioning correctly.
- **FAILED**: Check the logs for "AssertionError" or connection issues.

## Scenarios Covered
1. **Normal Flow**: Standard greeting -> Safe response.
2. **VR Warning**: VR context -> Response with mindfulness warning.
3. **Safety Block**: High-risk context -> Safe refusal ("I can't go down that path...").
4. **Karma Rewrite**: Low karma -> Soft redirect ("Let's focus on...").
