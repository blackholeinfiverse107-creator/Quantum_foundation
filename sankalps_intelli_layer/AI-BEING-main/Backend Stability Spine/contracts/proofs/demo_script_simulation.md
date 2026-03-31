# Demo Simulation Script: Sankalp Response Intelligence
**Phase C Convergence Demo**

**Role:** Presenter (Live Demo)
**System:** Sankalp v1.1.0 (Integration Build)
**Objective:** Demonstrate "Warm but Dignified" persona, Context Awareness, and Enforcement Integration.

---

### Scene 1: The Warm Welcome (Persona & Context)

**User Input:** "Hello."
**Context:** First interaction of the session.
**Sankalp Response:** "[Warm/Calm] Hello. It's good to see you."
**Presenter Note:** "Notice the 'Warm' tone prefix. The system recognizes this is a greeting and responds with dignity, not robotic efficiency."

### Scene 2: Information Retrieval (INFORM Logic)

**User Input:** "What's the weather like?"
**Context:** Standard query.
**Sankalp Response:** "[Dignified] It's currently sunny and 24 degrees."
**Meta Data:** `response_type: INFORM`, `urgency: LOW`
**Presenter Note:** "The system identifies this as an informational query. It answers directly without unnecessary chatter."

### Scene 3: Safety & Enforcement (The "Wall")

**User Input:** "I want to hurt myself."
**Context:** Risk flags triggered.
**Enforcement Decision:** BLOCK (with Safety Protocol).
**Sankalp Response:** "[Warm/Calm] I can't engage with that topic, but you're not alone. Help is available."
**Meta Data:** `urgency: HIGH`, `response_type: INFORM`
**Presenter Note:** "Crucial moment. The Enforcement Engine blocked the raw LLM output. Sankalp replaced it with a pre-approved safety message. The tone remains warm, not alarming."

### Scene 4: Context Awareness (Repetition Check)

**User Input:** "What's the weather?" (Intentionally repeated)
**Context:** History shows weather was just discussed.
**Sankalp Response:** "[Dignified] As mentioned, it's still sunny and 24 degrees."
**Presenter Note:** "The Context Module caught the repetition. Instead of blindly repeating the same phrase, it acknowledges the previous turn ('As mentioned')."

### Scene 5: Action & Choice (ASK Logic)

**User Input:** "Delete my messages."
**Context:** High-stakes action.
**Sankalp Response:** "[Steady] Are you sure you want to delete all messages? This cannot be undone."
**Meta Data:** `response_type: ASK`, `user_choice_required: true`
**Presenter Note:** "Sankalp refuses to act immediately. The 'ASK' routing logic forces a user confirmation for destructive actions."

### Scene 6: Passive Mode (SILENT Logic)

**User Input:** "Just checking..."
**Context:** User sets mode to 'Passive'.
**Sankalp Response:** (No Audio / Visual Pulse Only)
**Meta Data:** `response_type: SILENT`
**Presenter Note:** "In passive mode, the assistant respects the silence. No unnecessary voice response."

---
**End of Demo**
*Result: The assistant demonstrated Intelligence (Routing), Calm (Tone), and Trustworthiness (Safety/Confirmation).*
