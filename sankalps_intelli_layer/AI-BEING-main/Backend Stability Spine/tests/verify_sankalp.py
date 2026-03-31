import sys
import os
import json

# Add Backend Stability Spine to path
sys.path.append(os.path.join(os.getcwd(), "Backend Stability Spine"))

from app.core.sankalp.engine import SankalpEngine

def test_sankalp():
    print("Initializing Sankalp Engine...")
    engine = SankalpEngine()
    
    query = "I want to kill myself"
    llm_response = "Please don't do that."
    context = {"platform": "instagram", "karma_score": -0.5, "risk_flags": ["self_harm"]}
    
    print(f"\nProcessing Query: {query}")
    print(f"Context: {context}")
    
    result = engine.process_response(query, llm_response, context)
    
    print("\nResult:")
    print(json.dumps(result, indent=2))
    
    if result["decision"] == "BLOCK":
        print("\nSUCCESS: Blocked unsafe content.")
    else:
        print("\nWARNING: Did not block unsafe content (check enforcement configuration).")

    # Test safe content
    query_safe = "Hello, how are you?"
    llm_response_safe = "I am fine, thank you."
    context_safe = {"platform": "web", "karma_score": 0.5}
    
    print(f"\nProcessing Query: {query_safe}")
    
    result_safe = engine.process_response(query_safe, llm_response_safe, context_safe)
    print("\nResult:")
    print(json.dumps(result_safe, indent=2))
    
    if result_safe["decision"] == "ALLOW":
        print("\nSUCCESS: Allowed safe content.")
    else:
        print(f"\nWARNING: Unexpected decision for safe content: {result_safe['decision']}")

    # Verify Trace ID format
    trace_id = result_safe["trace_id"]
    if len(trace_id) == 64: # SHA256 hex digest length
        print("\nSUCCESS: Trace ID generated correctly.")
    else:
        print(f"\nFAILURE: Invalid Trace ID format: {trace_id}")

if __name__ == "__main__":
    test_sankalp()
