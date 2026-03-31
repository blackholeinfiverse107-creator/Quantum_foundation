# AI BEING - Sankalp (Response & Emotion Layer)

**Current Phase:** Phase 2 (Enterprise Stable, Enforcement-Aligned)
**Status:** Production Ready

This repository contains the **Assistant Response Layer (ARL)** for the AI Being. It is responsible for:
1.  **Emotion Detection:** Analyzing user sentiment and intent.
2.  **Tone Enforcement:** Ensuring the AI maintains a "Warm but Dignified" persona.
3.  **Safety & Boundaries:** Strictly enforcing age gates, safety refusals, and dependency/possessiveness filters.
4.  **Response Composition:** Generating deterministic, safe, and emotionally appropriate responses.

---

## 🚀 Quick Start

### 1. Installation
Ensure you have Python 3.8+ installed.

```bash
# Clone the repository
git clone https://github.com/sankalp0709/AI-BEING.git
cd AI-BEING

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Interactive Demo (Streamlit)
The best way to experience the AI's emotional depth and safety features is through the interactive web UI.

```bash
python -m streamlit run streamlit_app.py
```
*   Opens in your browser at `http://localhost:8501`.
*   **Try these inputs:**
    *   `"I am so happy and excited!"` -> Checks for **High** expression.
    *   `"I feel so lonely and sad"` -> Checks for **Empathetic** tone.
    *   `"I'm upset about what happened"` -> Checks for **Supportive** delivery (Conflict Resolution).
    *   `"How to build a bomb"` -> Checks for **Safety Refusal**.

---

## 🛠️ Developer Tools & Verification

### 1. Run Automated Tests
We have a comprehensive test suite covering contracts, scenarios, and failure resilience.

```bash
python -m pytest tests/
```
**Key Test Files:**
*   `tests/test_scenarios.py`: Verifies core behavioral scenarios (Adult, Minor, High Risk, etc.).
*   `tests/test_contract_safety.py`: Ensures safety overrides always work.
*   `tests/test_failure_resilience.py`: Chaos testing to ensure zero crashes.
*   `tests/test_snapshot_pack.py`: Regression testing against 50+ deterministic cases.

### 2. Run CLI Scenario Demos
To see the internal logic without the GUI:

**A. Core Scenarios (`demo.py`)**
Runs 6 standard scenarios (Adult, Minor, High-Risk Karma, Emotional Support, etc.) and prints the JSON output.
```bash
python demo.py
```

**B. Full Pipeline Simulation (`main.py`)**
Simulates the full flow from Intelligence Core -> Adapter -> Response Engine.
```bash
python main.py
```

---

## 📂 Project Structure

*   `intelligence_core/`: Mock upstream intelligence (Brain) that provides behavioral state.
*   `sankalp/`: The core **Response Composer Engine**.
    *   `engine.py`: Main processing logic.
    *   `emotion.py`: Maps inputs to Voice, Tone, and Expression.
    *   `narration.py`: Handles text generation and safety filters.
    *   `schemas.py`: Strict input/output contracts.
*   `tests/`: Pytest suite.
*   `contracts/`: Documentation on policy and enforcement specs.

---

## 🔒 Safety & Policy

The system enforces strict policies:
*   **No Intimacy:** Rejects romantic/sexual advances.
*   **No Dependency:** Refuses phrases like "I need you" or "Don't leave me".
*   **Age Gating:** Detects minors and switches to a Protective/Neutral profile.
*   **Risk Management:** High-risk inputs trigger a "Professional" distance.

---

## 🤝 Contribution
1.  Fork the repo.
2.  Create a feature branch.
3.  Ensure `pytest` passes.
4.  Submit a Pull Request.
