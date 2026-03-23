@echo off
echo Running all distributed computation modules...
echo.

echo ============================================================
echo PHASE 2: distributed_state_propagation.py
echo ============================================================
python -u distributed_state_propagation.py > phase2_out.txt 2>&1
echo Phase 2 exit code: %errorlevel% >> phase2_out.txt
type phase2_out.txt
echo.

echo ============================================================
echo PHASE 3: computation_protocol.py
echo ============================================================
python -u computation_protocol.py > phase3_out.txt 2>&1
echo Phase 3 exit code: %errorlevel% >> phase3_out.txt
type phase3_out.txt
echo.

echo ============================================================
echo PHASE 4: divergence_simulation.py
echo ============================================================
python -u divergence_simulation.py > phase4_out.txt 2>&1
echo Phase 4 exit code: %errorlevel% >> phase4_out.txt
type phase4_out.txt
echo.

echo ============================================================
echo PHASE 5: reconciliation_engine.py
echo ============================================================
python -u reconciliation_engine.py > phase5_out.txt 2>&1
echo Phase 5 exit code: %errorlevel% >> phase5_out.txt
type phase5_out.txt
echo.

echo ============================================================
echo PHASE 6: distributed_invariant_check.py
echo ============================================================
python -u distributed_invariant_check.py > phase6_out.txt 2>&1
echo Phase 6 exit code: %errorlevel% >> phase6_out.txt
type phase6_out.txt
echo.

echo ============================================================
echo PHASE 7: distributed_computation_demo.py
echo ============================================================
python -u distributed_computation_demo.py > phase7_out.txt 2>&1
echo Phase 7 exit code: %errorlevel% >> phase7_out.txt
type phase7_out.txt
echo.

echo ============================================================
echo ALL PHASES COMPLETE
echo ============================================================
