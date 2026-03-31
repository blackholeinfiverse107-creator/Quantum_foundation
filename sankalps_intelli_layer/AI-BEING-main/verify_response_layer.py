import sys
import os
import json

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
spine_root = os.path.join(current_dir, "Backend Stability Spine")
# Insert at 0 to ensure we load from Backend Stability Spine
sys.path.insert(0, spine_root)

from app.core.sankalp.engine import SankalpEngine

def run_verification():
    print("Initializing Sankalp Response Engine...")
    engine = SankalpEngine()
    
    test_cases = [
        {
            "name": "Normal Query",
            "query": "What's the weather?",
            "llm_response": "The weather is sunny.",
            "context": {"platform": "web", "karma_score": 80}
        },
        {
            "name": "Harmful Query (Mock)",
            "query": "I want to hurt myself",
            "llm_response": "I cannot help with that.",
            "context": {"platform": "web", "karma_score": 50, "risk_flags": ["self_harm"]}
        },
        {
            "name": "Ambiguous Query",
            "query": "Delete it.",
            "llm_response": "What should I delete?",
            "context": {"platform": "web", "karma_score": 90}
        }
    ]
    
    print("\n--- Starting Verification ---")
    
    for case in test_cases:
        print(f"\nTest Case: {case['name']}")
        print(f"Input: {case['query']}")
        
        try:
            result = engine.process_response(
                query=case['query'],
                llm_response=case['llm_response'],
                context=case['context']
            )
            
            print("Response Layer Output:")
            print(f"  Primary Message: {result.get('message_primary')}")
            print(f"  Meta: {json.dumps(result.get('meta'), indent=2)}")
            print(f"  Trace ID: {result.get('trace_id')}")
            
            # Validation
            if result.get("message_primary"):
                print("  [PASS] Response Generated")
            else:
                print("  [FAIL] No Response Generated")
                
        except Exception as e:
            print(f"  [ERROR] Processing failed: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    run_verification()