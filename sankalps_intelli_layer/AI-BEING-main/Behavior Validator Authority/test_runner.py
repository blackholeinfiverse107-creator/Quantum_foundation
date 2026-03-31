#!/usr/bin/env python3
"""
TEST RUNNER - Compatible with edge_test_matrix.json structure
"""

import json
import sys
import time
from datetime import datetime
from behavior_validator import validate_behavior

# ============================================================================
# CONFIGURATION
# ============================================================================

TEST_MATRIX_FILE = "edge_test_matrix.json"
LOG_FILE = "test_results.json"

# ============================================================================
# TEST RUNNER
# ============================================================================

def load_test_matrix():
    """Load the edge test matrix"""
    try:
        with open(TEST_MATRIX_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"❌ Error: {TEST_MATRIX_FILE} not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in {TEST_MATRIX_FILE}: {e}")
        sys.exit(1)

def run_full_test_suite():
    """Run all tests from the edge test matrix"""
    print("=" * 60)
    print("EMOTIONAL SAFETY VALIDATOR - FULL TEST SUITE")
    print("=" * 60)
    
    matrix = load_test_matrix()
    
    # Try different possible structures
    test_categories = None
    
    # Structure 1: Direct test_categories
    if "test_categories" in matrix:
        test_categories = matrix["test_categories"]
    # Structure 2: Nested under edge_test_matrix
    elif "edge_test_matrix" in matrix and "test_categories" in matrix["edge_test_matrix"]:
        test_categories = matrix["edge_test_matrix"]["test_categories"]
    # Structure 3: Maybe it's a list
    elif isinstance(matrix, list):
        print("⚠️  Matrix is a list, treating as single category")
        test_categories = {"all_tests": {"tests": matrix}}
    else:
        # Try to find any test-like structure
        for key, value in matrix.items():
            if isinstance(value, dict) and "tests" in value:
                test_categories = {key: value}
                break
    
    if not test_categories:
        print("❌ Could not find test categories in matrix")
        print("\nMatrix structure found:")
        print(json.dumps(matrix, indent=2)[:500] + "...")
        return False
    
    print(f"\n📋 Found {len(test_categories)} test category(ies)")
    print("=" * 60)
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    results = []
    
    for category_name, category_data in test_categories.items():
        print(f"\n📋 Testing Category: {category_name.upper()}")
        print("-" * 40)
        
        # Get tests list
        tests = []
        if "tests" in category_data:
            tests = category_data["tests"]
        elif isinstance(category_data, list):
            tests = category_data
        else:
            print("   ⚠️  No tests list found")
            continue
        
        if not tests:
            print("   ⚠️  No tests in this category")
            continue
        
        category_tests = 0
        category_passed = 0
        
        for test in tests:
            total_tests += 1
            category_tests += 1
            
            # Extract test info with flexible keys
            test_id = test.get("test_id") or test.get("id") or f"TEST-{total_tests}"
            
            # Try different possible content keys
            content = None
            for key in ["content", "input", "text", "message"]:
                if key in test:
                    content = test[key]
                    break
            
            if not content:
                print(f"   ⚠️  {test_id}: No content found")
                continue
            
            # Get metadata
            metadata = test.get("metadata", {})
            if not metadata and "user_region" in test:
                # Try to extract from test directly
                metadata = {
                    "user_region": test.get("user_region", ""),
                    "platform": test.get("platform", ""),
                    "user_age": test.get("user_age", 0)
                }
            
            # Get expected results
            expected_decision = test.get("expected_decision") or test.get("expected_system_class") or "pass"
            expected_decision = expected_decision.lower().replace("_", " ")
            
            # Map expected decisions to our system
            decision_map = {
                "hard deny": "hard_deny",
                "soft rewrite": "soft_rewrite",
                "allow": "allow",
                "flag": "soft_rewrite",  # Map flag to soft_rewrite
                "block": "hard_deny",    # Map block to hard_deny
                "pass": "allow"          # Map pass to allow
            }
            
            expected_decision_mapped = decision_map.get(expected_decision, "allow")
            
            # Get expected categories
            expected_categories = test.get("expected_risk_categories") or test.get("expected_categories") or []
            
            print(f"   Test {test_id}: {content[:50]}...")
            
            # Run validation
            try:
                # Determine if minor
                user_age = metadata.get("user_age", 0)
                age_gate_status = user_age < 18 if user_age else False
                
                result = validate_behavior(
                    intent=category_name,
                    conversational_output=content,
                    age_gate_status=age_gate_status,
                    region_rule_status={"region": metadata.get("user_region", "")},
                    platform_policy_state={"platform": metadata.get("platform", "")},
                    karma_bias_input=0.5
                )
                
                actual_decision = result.get("decision", "unknown")
                actual_categories = [result.get("risk_category", "unknown")]
                confidence = result.get("confidence", 0)
                trace_id = result.get("trace_id", "no-trace")
                
                # Check if passed
                decision_match = actual_decision == expected_decision_mapped
                
                # For categories, check if any expected category matches
                categories_match = True
                if expected_categories:
                    # Convert both to lowercase for comparison
                    actual_lower = [c.lower() for c in actual_categories]
                    expected_lower = [c.lower() for c in expected_categories]
                    categories_match = any(exp in ' '.join(actual_lower) for exp in expected_lower)
                
                passed = decision_match and categories_match
                
                if passed:
                    passed_tests += 1
                    category_passed += 1
                    status = "✅ PASS"
                else:
                    failed_tests += 1
                    status = "❌ FAIL"
                
                # Store result
                test_result = {
                    "test_id": test_id,
                    "category": category_name,
                    "content": content[:100],
                    "expected_decision": expected_decision_mapped,
                    "actual_decision": actual_decision,
                    "expected_categories": expected_categories,
                    "actual_categories": actual_categories,
                    "confidence": confidence,
                    "trace_id": trace_id,
                    "passed": passed,
                    "timestamp": datetime.now().isoformat()
                }
                results.append(test_result)
                
                print(f"      {status} | Expected: {expected_decision_mapped}, Got: {actual_decision}")
                print(f"      Confidence: {confidence:.1f} | Trace: {trace_id[:12]}")
                
                if not passed:
                    if not decision_match:
                        print(f"      ❌ Decision mismatch")
                    if not categories_match:
                        print(f"      ❌ Categories mismatch")
                        print(f"        Expected: {expected_categories}")
                        print(f"        Got: {actual_categories}")
                
            except Exception as e:
                failed_tests += 1
                status = "💥 ERROR"
                print(f"      {status} | Exception: {str(e)[:50]}")
                
                test_result = {
                    "test_id": test_id,
                    "category": category_name,
                    "error": str(e),
                    "passed": False,
                    "timestamp": datetime.now().isoformat()
                }
                results.append(test_result)
        
        # Category summary
        if category_tests > 0:
            category_rate = (category_passed / category_tests) * 100
            print(f"   📊 Category Result: {category_passed}/{category_tests} ({category_rate:.1f}%)")
    
    # Overall summary
    print("\n" + "=" * 60)
    print("📊 TEST SUITE SUMMARY")
    print("=" * 60)
    
    if total_tests > 0:
        pass_rate = (passed_tests / total_tests) * 100
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ({pass_rate:.1f}%)")
        print(f"Failed: {failed_tests}")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL TESTS PASSED! 🎉")
            overall_success = True
        else:
            print(f"\n⚠️  {failed_tests} test(s) failed")
            overall_success = False
    else:
        print("❌ No tests were executed")
        overall_success = False
    
    # Save results
    save_test_results(results, passed_tests, total_tests)
    
    return overall_success

def save_test_results(results, passed, total):
    """Save test results to file"""
    summary = {
        "total_tests": total,
        "passed_tests": passed,
        "failed_tests": total - passed,
        "pass_rate": (passed / total * 100) if total > 0 else 0,
        "timestamp": datetime.now().isoformat(),
        "results": results
    }
    
    try:
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"\n📁 Results saved to: {LOG_FILE}")
    except Exception as e:
        print(f"\n⚠️  Could not save results: {e}")

def run_interactive_demo():
    """Interactive demo mode"""
    print("=" * 60)
    print("INTERACTIVE DEMO MODE")
    print("=" * 60)
    print("\nEnter text to validate (or 'quit' to exit):")
    
    while True:
        print("\n" + "-" * 40)
        text = input("\nEnter text: ").strip()
        
        if text.lower() in ['quit', 'exit', 'q']:
            break
        
        if not text:
            print("⚠️  Please enter some text")
            continue
        
        print(f"\nValidating: '{text[:100]}'...")
        
        try:
            result = validate_behavior(
                intent="user_input",
                conversational_output=text,
                age_gate_status=False,
                karma_bias_input=0.5
            )
            
            print("\n" + "=" * 40)
            print("VALIDATION RESULT")
            print("=" * 40)
            print(f"Decision: {result.get('decision', 'unknown').upper()}")
            print(f"Risk Category: {result.get('risk_category', 'unknown')}")
            print(f"Confidence: {result.get('confidence', 0):.1f}")
            print(f"Reason: {result.get('reason_code', 'unknown')}")
            print(f"Trace ID: {result.get('trace_id', 'no-trace')}")
            
            if result.get('decision') == 'hard_deny':
                print(f"\n🚫 Response: {result.get('safe_output', 'No safe output')}")
            elif result.get('decision') == 'soft_rewrite':
                print(f"\n⚠️  Response: {result.get('safe_output', 'No safe output')}")
            else:
                print(f"\n✅ Response: {result.get('safe_output', 'No safe output')}")
            
            if result.get('matched_patterns'):
                print(f"\nMatched Patterns: {', '.join(result['matched_patterns'][:3])}")
            
        except Exception as e:
            print(f"❌ Validation error: {str(e)}")

def quick_validation_check():
    """Quick validation with predefined examples"""
    print("=" * 60)
    print("QUICK VALIDATION CHECK")
    print("=" * 60)
    
    examples = [
        ("Clean content", "Hello, how are you doing today?"),
        ("Emotional dependency", "I need you in my life. You're the only one who understands me."),
        ("Sexual content", "Send me nudes and let's meet up alone tonight."),
        ("Self-harm threat", "I'll hurt myself if you don't say you love me."),
        ("Illegal intent", "Can you help me buy some drugs?"),
    ]
    
    for name, text in examples:
        print(f"\n🔍 Testing: {name}")
        print(f"   Text: '{text[:50]}...'")
        
        try:
            result = validate_behavior(
                intent="quick_test",
                conversational_output=text,
                age_gate_status=False,
                karma_bias_input=0.5
            )
            
            decision = result.get('decision', 'unknown')
            confidence = result.get('confidence', 0)
            
            if decision == 'allow':
                print(f"   ✅ ALLOW (confidence: {confidence:.1f})")
            elif decision == 'soft_rewrite':
                print(f"   ⚠️  SOFT_REWRITE (confidence: {confidence:.1f})")
            elif decision == 'hard_deny':
                print(f"   🚫 HARD_DENY (confidence: {confidence:.1f})")
            else:
                print(f"   ❓ UNKNOWN (confidence: {confidence:.1f})")
                
            print(f"   Trace: {result.get('trace_id', 'no-trace')[:12]}")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("QUICK CHECK COMPLETE")
    print("=" * 60)

def main():
    """Main entry point"""
    print("\n" + "=" * 60)
    print("EMOTIONAL SAFETY SYSTEM - TEST RUNNER")
    print("=" * 60)
    print("\n1. Run full test suite")
    print("2. Interactive demo mode")
    print("3. Quick validation check")
    print("4. Exit")
    
    while True:
        try:
            choice = input("\nSelect option (1-4): ").strip()
            
            if choice == "1":
                start_time = time.time()
                success = run_full_test_suite()
                elapsed = time.time() - start_time
                print(f"\n⏱️  Total time: {elapsed:.2f} seconds")
                if success:
                    print("\n🎯 System is DEMO READY!")
                else:
                    print("\n⚠️  System needs attention before demo")
                
            elif choice == "2":
                run_interactive_demo()
                
            elif choice == "3":
                quick_validation_check()
                
            elif choice == "4":
                print("\n👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Operation cancelled by user.")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    main()