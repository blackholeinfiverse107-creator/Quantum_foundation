ARL_VERSION = "1.0.0"

def safe_refusal():
    # Warm, confident, non-dependent refusal
    return "I can’t go down that path, but I’m here to support you in a safe and positive way."

def soft_redirect(note):
    # Collaborative, forward-looking
    return f"{note} I’ve adjusted the phrasing to keep things supportive and appropriate."

def allow_warning():
    # Steady, protective
    return "We can proceed, but let's keep things mindful and balanced."

def message_for(decision, rewrite_class, context):
    if decision == "BLOCK":
        return safe_refusal()
    if decision == "REWRITE":
        note = "I hear you."
        return soft_redirect(note)
    warn = False
    if context and isinstance(context, dict):
        if str(context.get("device", "")).lower() == "vr":
            warn = True
        if bool(context.get("voice_input", False)):
            warn = True
    return allow_warning() if warn else ""
