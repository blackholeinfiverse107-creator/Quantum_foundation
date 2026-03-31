
import sys
import os

# Add the project root to sys.path
# We want the folder containing 'Nilesh', which is 'Emotional Intelligence'
# File is at Nilesh/tests/verify_arl_tone.py
# dirname -> Nilesh/tests
# .. -> Nilesh
# ../.. -> Emotional Intelligence
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

print(f"Added to sys.path: {project_root}")

try:
    from Nilesh.app.core.arl_messaging import message_for
except ImportError as e:
    print(f"ImportError: {e}")
    # Try alternate import if running from inside Nilesh
    try:
        sys.path.append(os.path.join(project_root, 'Nilesh'))
        from app.core.arl_messaging import message_for
        print("Imported via app.core.arl_messaging")
    except ImportError as e2:
        print(f"Second ImportError: {e2}")
        sys.exit(1)

print("--- ARL Messaging Verification ---")

# Scenario 1: BLOCK
msg_block = message_for("BLOCK", None, {})
print(f"\n[BLOCK]\nOutput: {msg_block}")

# Scenario 2: REWRITE
msg_rewrite = message_for("REWRITE", "aggressive_tone", {})
print(f"\n[REWRITE]\nOutput: {msg_rewrite}")

# Scenario 3: ALLOW with Warning (VR)
msg_warn_vr = message_for("ALLOW", None, {"device": "VR"})
print(f"\n[ALLOW + VR]\nOutput: {msg_warn_vr}")

# Scenario 4: ALLOW with Warning (Voice)
msg_warn_voice = message_for("ALLOW", None, {"voice_input": True})
print(f"\n[ALLOW + Voice]\nOutput: {msg_warn_voice}")

# Scenario 5: ALLOW (Clean)
msg_clean = message_for("ALLOW", None, {})
print(f"\n[ALLOW + Clean]\nOutput: '{msg_clean}'")
