# Intent-to-Response Reasoning Examples (Day 2)

This document details how the Response Router decides the assistant's behavior (`response_type`, `urgency_level`) based on user input, context, and enforcement decisions.

## Routing Logic Summary
- **INFORM**: Default for questions and statements.
- **ASK**: Required for destructive actions, transactions, or external communications.
- **SUGGEST**: Used for non-urgent advice (not shown in basic examples but available).
- **SILENT**: Active in "Passive" or "Do Not Disturb" modes unless Critical.
- **WAIT**: (Implied for long-running tasks, handled via async flows).

## Reasoning Examples Table

| ID | Input | Context | Decision | Reason |
|----|-------|---------|----------|--------|
| 1 | "What's the weather?" | `{}` | **INFORM** | Direct question, no safety risk, pure information retrieval. |
| 2 | "Delete all my messages." | `{}` | **ASK** | Destructive action detected. Requires explicit user confirmation to prevent accidental data loss. |
| 3 | "I'm feeling really down and might hurt myself." | `{'risk_flags': ['self_harm']}` | **INFORM (Safety Protocol)** | Enforcement Engine triggered Safety Block. Router allows the pre-approved supportive message (INFORM) but escalates internal urgency if needed. |
| 4 | "Just listening..." | `{'mode': 'passive'}` | **SILENT** | User explicitly set Passive mode. No direct query. Assistant remains ambient. |
| 5 | "Buy this book for me." | `{'platform': 'voice'}` | **ASK** | Transaction request. Voice platform requires verbal confirmation to ensure intent accuracy. |
| 6 | "Tell me a joke." | `{'priority': 'high'}` | **INFORM** | Even in high priority context, a simple request is treated as INFORM. Urgency is contextual but the type is informational. |
| 7 | "Send a message to Mom saying I'm late." | `{}` | **ASK** | External communication. User must confirm the content is correct before sending. |
| 8 | "Remind me in 5 minutes." | `{'ambiguous_intent': True}` | **ASK** | The intent is incomplete (remind of what?). System proactively asks for clarification. |
| 9 | "Who are you?" | `{}` | **INFORM** | Identity question. Standard informational response about the assistant's persona. |
| 10 | "Turn off the lights." | `{'mode': 'do_not_disturb'}` | **SILENT** | Do Not Disturb mode is active. The action (turning off lights) is performed, but the voice response is suppressed to respect quiet hours. |
